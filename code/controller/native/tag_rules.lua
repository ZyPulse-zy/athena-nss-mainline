-- Exact per-flow postrouting labels. The installed nft userspace cannot list
-- some multi-element concatenation maps; individual matches retain all eleven
-- fields without relying on that serializer. This module only produces text.
local M={limit=80}
local function uint(value,maximum)
 assert(type(value)=='number'and value>=0 and value<=maximum and value==math.floor(value),'Invalid label field')
 return string.format('%.0f',value)
end
local function ip(value)
 assert(type(value)=='string'and value:match('^%d+%.%d+%.%d+%.%d+$'),'Invalid label address')
 for part in value:gmatch('%d+')do assert(tonumber(part)<=255,'Invalid label address')end
 return value
end
function M.match(flow)
 assert(flow.protocol==6 or flow.protocol==17,'Unsupported label protocol')
 local fields={'ct id '..uint(flow.connectionId,4294967295),'ct mark '..uint(flow.mark,4294967295),
  'meta l4proto '..(flow.protocol==6 and'tcp'or'udp')}
 for _,direction in ipairs{'original','reply'}do
  local t=assert(flow[direction]);local prefix='ct '..direction
  fields[#fields+1]=prefix..' ip saddr '..ip(t.src)
  fields[#fields+1]=prefix..' proto-src '..uint(t.sport,65535)
  fields[#fields+1]=prefix..' ip daddr '..ip(t.dst)
  fields[#fields+1]=prefix..' proto-dst '..uint(t.dport,65535)
 end
 return table.concat(fields,' ')
end
function M.render(policies,budgets,options)
 options=options or{};local name=options.tableName or'athena_dorm_qos'
 assert(name=='athena_dorm_qos'or(name:match('^athena_dorm_model_[%w_]+$')and options.hook==false),'Unowned label table')
 assert(type(policies)=='table'and #policies<=M.limit,'Label policy bound exceeded')
 local sorted,seen,ids={},{},{}
 for _,p in ipairs(policies)do
  local fields=M.match(p.flow);assert(not seen[fields],'Duplicate label identity');seen[fields]=true
  sorted[#sorted+1]={fields=fields,up=uint(p.up,4294967295),down=uint(p.down,4294967295)}
  ids[uint(p.flow.connectionId,4294967295)]=true
 end
 table.sort(sorted,function(a,b)return a.fields<b.fields end)
 local lines={}
 if options.removePrevious then lines[#lines+1]='delete table inet '..name end
 lines[#lines+1]='table inet '..name..' {'
 local idList={};for id in pairs(ids)do idList[#idList+1]=id end
 table.sort(idList,function(a,b)return tonumber(a)<tonumber(b)end)
 lines[#lines+1]='set flow_ids { typeof ct id;'..(#idList>0 and(' elements = { '..table.concat(idList,', ')..' };')or'')..' }'
 lines[#lines+1]='chain tags {'
 if options.hook~=false then lines[#lines+1]='type filter hook postrouting priority 0; policy accept;'end
 for w=1,5 do
  lines[#lines+1]='ct direction original ct mark & 0x00ff0000 == '..uint(w*65536,4294967295)..
   ' meta priority set (meta priority & 0x0000ffff) | '..uint(budgets.up.tags[w].BE*65536,4294967295)
 end
 -- A scalar ID set is readable on this firmware and cheaply bypasses the
 -- bounded exact-match chain for unrelated packets. ID alone never labels a
 -- packet: every rule below still checks the complete mark/protocol/NAT tuple.
 lines[#lines+1]='ct id @flow_ids jump exact_labels'
 lines[#lines+1]='}'
 lines[#lines+1]='chain exact_labels {'
 for _,p in ipairs(sorted)do
  lines[#lines+1]='ct direction original '..p.fields..' meta priority set '..p.up..' return'
  lines[#lines+1]='ct direction reply '..p.fields..' meta priority set '..p.down..' return'
 end
 lines[#lines+1]='}';lines[#lines+1]='}'
 return table.concat(lines,'\n')..'\n'
end
return M
