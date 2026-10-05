local j=require('luci.jsonc');local checks={};local expected=normalize(PLAN.expected,PLAN)
local function clone(x)return assert(j.parse(j.stringify(x)))end
local function test(name,edit,want)
 local x=clone(NATIVE);edit(x);local ok,s=pcall(normalize,x,PLAN);assert((ok and s==expected)==want,name)
 checks[#checks+1]={name=name,passed=true,simulated=true,accepted=want}
end
test('recorded-native-identity-with-simulated-up-tags',function()end,true)
local names={'tcp_writer_up','udp_writer_up','tcp_writer_down','udp_writer_down'}
local function rule(x,name)for _,v in ipairs(x.nftables)do if v.rule and v.rule.comment==PLAN.owner..':'..name then return v.rule end end;error('No rule '..name)end
for _,name in ipairs(names)do
 test(name..'-zero-rejected',function(x)for _,e in ipairs(rule(x,name).expr)do if e.mangle then e.mangle.value=0 end end end,false)
 test(name..'-other-direction-tag-rejected',function(x)for _,e in ipairs(rule(x,name).expr)do if e.mangle then e.mangle.value=name:find('_up',1,true)and 0x8f060000 or 0x8e060000 end end end,false)
 test(name..'-other-class-tag-rejected',function(x)for _,e in ipairs(rule(x,name).expr)do if e.mangle then local t=name:find('_up',1,true)and 0x8e050000 or 0x8f050000;e.mangle.value=name:find('tcp_',1,true)and(t+0x10000)or t end end end,false)
 test(name..'-outside-writer-rejected',function(x)rule(x,name).chain='post'end,false)
end
test('numeric-nss-tags-normalize',function(x)for _,name in ipairs(names)do local a={tcp_writer_up=0x8e050000,udp_writer_up=0x8e060000,tcp_writer_down=0x8f050000,udp_writer_down=0x8f060000};for _,e in ipairs(rule(x,name).expr)do if e.mangle then e.mangle.value=a[name]end end end end,true)
test('unknown-comment-unknown-tag-rejected',function(x)local r=rule(x,'tcp_writer_up');r.comment=PLAN.owner..':foreign';for _,e in ipairs(r.expr)do if e.mangle then e.mangle.value='unknown'end end end,false)
test('foreign-owner-rejected',function(x)rule(x,'tcp_writer_up').comment='foreign-owner'end,false)
for _,key in ipairs({'id','mark','zone','protocol'})do test('ct-'..key..'-drift-rejected',function(x)for _,e in ipairs(rule(x,'tcp_writer_up').expr)do if e.match and e.match.left.ct and e.match.left.ct.key==key then e.match.right=key=='zone'and 1 or 0;return end end;error('No CT field')end,false)end
for _,key in ipairs({'iifname','oifname'})do test(key..'-drift-rejected',function(x)for _,e in ipairs(rule(x,'tcp_writer_up').expr)do if e.match and e.match.left.meta and e.match.left.meta.key==key then e.match.right='foreign';return end end;error('No interface')end,false)end
test('foreign-nft-action-rejected',function(x)local r=rule(x,'tcp_writer_up');r.expr[#r.expr+1]={accept={}}end,false)
print(j.stringify({passed=true,checks=checks,actualKernelRecordIdentityRetained=true,uplinkTagsSimulated=true,configurationWrites=false,nssAdmissionAllowed=false}))
