import fs from 'node:fs';import assert from 'node:assert/strict';
import{connectRouter}from'../nss27/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss154',p=JSON.parse(fs.readFileSync(root+'/controlled-candidates-private.json')).pairs[0];assert.ok(p&&p.tcp.wan!==4);
const original=fs.readFileSync('work/nss49/read-prerequisites.lua','utf8');
const anchor="local s=f:read('*a');f:close();local b,r=s:match";
assert.equal(original.split(anchor).length,2);
const diagnostic=original.replace(anchor,"local s,err,errno=f:read('*a');local closeOk,closeWhy,closeCode=f:close();assert(s, 'READ_FAILED err='..tostring(err)..' errno='..tostring(errno)..' close='..tostring(closeOk)..'/'..tostring(closeWhy)..'/'..tostring(closeCode));local b,r=s:match");
const c=await connectRouter();try{const e=encode('/usr/bin/lua - '+p.tcp.wan+" <<'NSS154_READ_PREREQUISITE_DIAGNOSTIC'\n"+diagnostic+"\nNSS154_READ_PREREQUISITE_DIAGNOSTIC\n");const raw=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/prerequisite-diagnostic-private.json',JSON.stringify({raw,readonly:true,sameOriginalReadWithErrorDetailOnly:true},null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);const v=JSON.parse(raw.stdout);console.log(JSON.stringify({passed:true,readonly:true,selectedWan:v.wan,originalPrerequisiteFieldsPresent:true,readErrorReproduced:false}));}finally{c.close()}
