import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const source=fs.readFileSync('work/nss33/fast-path.lua','utf8'),fixture=fs.readFileSync('work/nss33/aba-fixtures.lua','utf8');
const runnable=source.split('\n').filter(x=>!x.trimStart().startsWith('--')).join('\n');
const code="local j=require('luci.jsonc');local Fast=assert(loadstring([====["+runnable+"]====]))()\n"+fixture;
const e=encode("/usr/bin/lua - <<'NSS32_ABA_FIXTURE'\n"+code+"\nNSS32_ABA_FIXTURE\n"),c=await connectRouter();let r;try{r=receipt(await c.run(e.command),e)}finally{c.close()}
fs.writeFileSync('work/nss33/aba-replay-raw-private.json',JSON.stringify(r,null,2));assert.equal(r.code,0,r.stderr);const result=JSON.parse(r.stdout);assert.equal(result.passed,true);result.sourceSha256=crypto.createHash('sha256').update(source).digest('hex');result.execBytes=e.execBytes;result.routerWrites=false;
fs.writeFileSync('work/nss33/aba-qualified.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
