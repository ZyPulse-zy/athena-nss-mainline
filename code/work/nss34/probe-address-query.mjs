import fs from 'node:fs';import assert from 'node:assert/strict';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const code=String.raw`local j=require('luci.jsonc');local n=require('nixio');local function now()local f=assert(io.open('/proc/uptime'));local s=f:read(128);f:close();return tonumber(s:match('^[%d.]+'))end
local rows={};for i=1,8 do local t=now();local f=assert(io.popen('/usr/bin/timeout -k 1 2 /bin/sh -c \'/sbin/ip -j -4 address show\'; r=$?; printf "\n__NSS34_RC__%s\n" "$r"'))
local raw=f:read(65665)or'';f:close();assert(#raw<=65664);local body,rc=raw:match('^(.*)\n__NSS34_RC__(%d+)\n$');local parsed=body and j.parse(body)
rows[#rows+1]={seconds=now()-t,rc=tonumber(rc),bytes=body and #body,parseable=type(parsed)=='table',interfaceCount=type(parsed)=='table'and #parsed or nil};n.nanosleep(1)end
print(j.stringify({routerWrites=false,trafficGenerated=false,rows=rows}))`;
const c=await connectRouter();try{const e=encode("/usr/bin/lua - <<'NSS34_ADDR_READONLY'\n"+code+"\nNSS34_ADDR_READONLY\n");const r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr);const out=JSON.parse(r.stdout);out.observedAt=new Date().toISOString();fs.writeFileSync('work/nss34/address-query-probe.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));}finally{c.close()}
