-- Preserve the complete original JSON projection, then bound each jsonc visit set.
-- This changes encoding work, not fields, publication, parser, source or expiry.
local function stringify(value,j,project)
 local p=project(value)
 local function object(t)
  if type(t)~='table'or next(t)==nil then return false end
  for k in pairs(t)do if type(k)~='string'then return false end end;return true
 end
 if not(object(p)and object(p.snapshot)and type(p.snapshot.flows)=='table')then return j.stringify(p)end
 local flows=p.snapshot.flows;local count=0
 for k in pairs(flows)do if type(k)~='number'or k%1~=0 or k<1 then return j.stringify(p)end;count=count+1 end
 if count~=#flows then return j.stringify(p)end
 local function enc(v)return assert(j.stringify(v))end
 local parts={}
 for _,flow in ipairs(flows)do parts[#parts+1]=enc(flow)end
 local encodedFlows='['..table.concat(parts,',')..']'
 parts={}
 for k,v in pairs(p.snapshot)do parts[#parts+1]=enc(k)..':'..(k=='flows'and encodedFlows or enc(v))end
 local encodedSnapshot='{'..table.concat(parts,',')..'}'
 parts={}
 for k,v in pairs(p)do parts[#parts+1]=enc(k)..':'..(k=='snapshot'and encodedSnapshot or enc(v))end
 return '{'..table.concat(parts,',')..'}'
end
return stringify
