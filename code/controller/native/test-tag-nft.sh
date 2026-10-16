#!/bin/sh
# Run beside tag_rules.lua/queue_plan.lua in a private target model directory.
# Only an independently named table with no packet hooks is ever installed.
set -eu
base=${0%/*}
nft=/usr/sbin/nft
temporary=$(mktemp -d /tmp/athena-dorm-label-test.XXXXXX)
chmod 700 "$temporary"
table="athena_dorm_model_nfttest_$$"
owned=0
cleanup() {
 if test "$owned" = 1; then
  "$nft" delete table inet "$table"
  owned=0
 fi
 # Keep only scratch diagnostics on a failed check; no production files touched.
}
trap cleanup EXIT HUP INT TERM
tables=$("$nft" list tables)
if printf '%s\n' "$tables" | awk -v wanted="$table" '$3 == wanted { found=1 } END { exit !found }'; then
 echo 'Model table already exists; inspect instead of overwriting' >&2
 exit 1
fi
for count in 0 2 80; do
 lua - "$base" "$count" "$table" "$temporary/policy.nft" <<'LUA'
local root,count,name,file=arg[1],assert(tonumber(arg[2])),arg[3],arg[4]
local m=dofile(root..'/tag_rules.lua');local p=dofile(root..'/queue_plan.lua')
local b={up=p.plan(0x7e00,{40000,40000,40000,40000,40000}),down=p.plan(0x7a00,{70000,70000,70000,70000,70000})}
local rows={}
for i=1,count do
 local w=(i-1)%5+1;local rt=i%2==0;local class=rt and'RT'or'BE';local low=rt and 6 or 0
 rows[i]={flow={connectionId=1000+i,mark=w*65536+256,protocol=rt and 17 or 6,
  original={src='192.0.2.12',sport=41000+i,dst='198.51.100.99',dport=27015},
  reply={src='198.51.100.99',sport=27015,dst='203.0.113.1',dport=50000+i}},
  up=b.up.tags[w][class]*65536+low,down=b.down.tags[w][class]*65536+low}
end
local text=m.render(rows,b,{tableName=name,hook=false})
assert(not text:find('hook',1,true)and not text:find('map ',1,true))
local f=assert(io.open(file,'w'));assert(f:write(text));assert(f:close())
LUA
 "$nft" -c -f "$temporary/policy.nft"
 owned=1
 "$nft" -f "$temporary/policy.nft"
 "$nft" list table inet "$table" > "$temporary/readback.nft"
 "$nft" -j list table inet "$table" > "$temporary/readback.json"
 "$nft" -c -f "$temporary/readback.nft"
 lua - "$count" "$temporary/readback.json" <<'LUA'
local j=require('luci.jsonc');local count=assert(tonumber(arg[1]));local f=assert(io.open(arg[2]));local d=assert(j.parse(f:read('*a')));f:close()
local rules,exact,values=0,0,{}
for _,row in ipairs(d.nftables)do
 if row.chain then assert(not row.chain.hook,'Model acquired a traffic hook')end
 if row.rule then
  rules=rules+1
  if row.rule.chain=='exact_labels'then
   exact=exact+1;local fields=0
   for _,e in ipairs(row.rule.expr)do
    if e.match then fields=fields+1 end
    if e.mangle and e.mangle.key and e.mangle.key.meta and e.mangle.key.meta.key=='priority'then
     local v=e.mangle.value
     if type(v)=='string'then local major,minor=v:match('^(%x+):(%x+)$');assert(major);v=tonumber(major,16)*65536+tonumber(minor,16)end
     values[#values+1]=v
    end
   end
   assert(fields==12,'Direction or full connection identity lost')
  end
 end
end
assert(rules==count*2+6 and exact==count*2)
local expected={}
for i=1,count do local w=(i-1)%5+1;local rt=i%2==0;local tag=rt and 6 or 5;local low=rt and 6 or 0
 expected[#expected+1]=(0x7e00+w*16+tag)*65536+low;expected[#expected+1]=(0x7a00+w*16+tag)*65536+low
end
table.sort(values);table.sort(expected);assert(#values==#expected)
for i,v in ipairs(values)do assert(v==expected[i],'Queue label value changed')end
print(j.stringify({passed=true,policies=count,rules=rules,fullIdentityAndLabelsPreserved=true,textAndJsonReadback=true,exportReparsed=true,noTrafficHooks=true,modelOnly=true}))
LUA
 cleanup
done
tables=$("$nft" list tables)
if printf '%s\n' "$tables" | awk -v wanted="$table" '$3 == wanted { found=1 } END { exit !found }'; then
 echo 'Model cleanup unconfirmed' >&2
 exit 1
fi
echo '{"passed":true,"cleanupConfirmed":true,"productionRulesChanged":false}'
