import fs from'node:fs';import crypto from'node:crypto';import assert from'node:assert/strict';
import{connectRouter}from'../nss27/connect-router.mjs';import{encode,receipt}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/v37-sim',fast=fs.readFileSync(root+'/fast-path.lua','utf8'),model=fs.readFileSync(root+'/align-probe-models.lua','utf8');
assert.equal(model.split('__FAST__').length,2);assert.ok(!fast.includes(']====]'));
const rendered="local j=require('luci.jsonc');\n"+model.replace('__FAST__',()=>fast);
const enc=encode("/usr/bin/lua - <<'V35_PROBE_MODEL_ONLY'\n"+rendered+"\nV35_PROBE_MODEL_ONLY\n");
const dir=root+'/probe-model-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
fs.writeFileSync(dir+'/rendered-private.lua',rendered,{flag:'wx'});
const c=await connectRouter();let raw;
try{raw=receipt(await c.run(enc.command),enc)}finally{c.close()}
fs.writeFileSync(dir+'/raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
assert.equal(raw.code,0,raw.stderr);const result=JSON.parse(raw.stdout);assert.ok(result.passed&&result.checks===7&&result.modelOnly&&!result.productionWrites);
const proof={...result,sourceSha256:crypto.createHash('sha256').update(fast).digest('hex'),modelSha256:crypto.createHash('sha256').update(model).digest('hex'),
 renderedSha256:crypto.createHash('sha256').update(rendered).digest('hex'),execBytes:enc.execBytes,rawBytes:enc.rawBytes,modelDirectory:dir,
 actualRamModels:true,actualProductionGateLoaded:false,rootCauseEstablished:false,routerProductionWrites:false};
fs.writeFileSync(root+'/probe-retention-qualified.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...proof,cases:undefined,modelDirectory:undefined}));
