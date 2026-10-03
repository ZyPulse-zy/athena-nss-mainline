import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss35',ctx=JSON.parse(fs.readFileSync('work/nss33/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const core=fs.readFileSync('work/nss28/classifier-core.lua');assert.equal(sha(core),cfg.files['classifier-core.lua']);
let code=fs.readFileSync('work/nss28/rendered-core-fixtures-part2.lua','utf8');assert.ok(code.includes(core.toString().trim()));
code=code.replace('maxSourceBytes=262144','maxSourceBytes=524288').replace('local function fresh()','local addressFault=false;local addressOffset=0\nlocal function fresh()');
code=code.replace("assert(cmd=='ip -j -4 address show');local a={}","assert(cmd=='ip -j -4 address show');if addressFault then error({kind='bounded-address-failure',queryCleanupCompleted=true},0)end;local a={}");
code=code.replace("['local']='198.51.100.'..w","['local']='198.51.100.'..(w+addressOffset)");
code=code.replace('local seq=c.provenance.sequence;',"local seq=c.provenance.sequence;addressFault=true;local ok,err=pcall(sample,step);yes(not ok and type(err)=='table'and err.kind=='bounded-address-failure','failed address discovery propagates without publishing a flow snapshot');addressFault=false;");
code=code.replace('print(j.stringify({passed=true',"addressOffset=10;local changed=sample(step);yes(#changed.flows==0,'new address inventory cannot reuse stale NAT addresses');print(j.stringify({passed=true");
code=code.replaceAll('overflow history discard','address-failure history discard').replaceAll('overflow does not reset','address failure does not reset').replaceAll('overflow reset preserves','address-failure reset preserves');
fs.writeFileSync(root+'/history-native-fixtures.lua',code);
const c=await connectRouter();try{
 const e=encode("/usr/bin/lua - <<'NSS35_HISTORY'\n"+code+"\nNSS35_HISTORY\n");const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/history-native-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr+' '+r.stdout);const d=JSON.parse(r.stdout);d.coreSha256=sha(core);d.execBytes=e.execBytes;d.scope='Exact deployed observer with synthetic conntrack rows and address failure; actual Lua/jsonc, no service mutation.';fs.writeFileSync(root+'/history-native-qualified.json',JSON.stringify(d,null,2)+'\n');console.log(JSON.stringify(d));
}finally{c.close()}
