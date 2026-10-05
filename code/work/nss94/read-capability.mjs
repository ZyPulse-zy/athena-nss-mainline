import fs from 'node:fs';
import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';
const c=await connectRouter();
try {
 const r=await c.run("/usr/bin/timeout -k 1 4 /usr/bin/lua - <<'NSS94_READ_ONLY_CAPABILITY'\nlocal j=require('luci.jsonc');local function run(c)local h=assert(io.popen(c));local s=h:read('*a');local ok=h:close();assert(ok);return j.parse(s)end;print(j.stringify({links=run('/sbin/ip -j -d link show'),cake=run('/sbin/tc -j -s -d qdisc show dev rpifb5'),ingress=run('/sbin/tc -j -s filter show dev rpwan5 ingress')}))\nNSS94_READ_ONLY_CAPABILITY\n");
 fs.writeFileSync('work/nss94/capability-private.json',JSON.stringify(r,null,2));assert.equal(r.code,0,r.stderr);const v=JSON.parse(r.stdout);
 console.log(JSON.stringify({links:v.links.map(x=>({ifname:x.ifname,ifindex:x.ifindex,link:x.link_index,info:x.linkinfo})),cake:v.cake,ingress:v.ingress,readonly:true}));
}finally{c.close()}
