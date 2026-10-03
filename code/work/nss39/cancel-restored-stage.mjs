import fs from'node:fs';import assert from'node:assert/strict';import{connectRouter}from'../nss20/connect-router.mjs';
const d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json')),q=JSON.parse(fs.readFileSync(d.localDir+'/rollback-qualified.json'));assert.ok(!d.committed&&q.passed&&q.automaticExpiryWithoutControllerRollback);
fs.writeFileSync(d.localDir+'/deployment-expired-reinstall.json',JSON.stringify({...d,reason:'Fixed commit reserve elapsed during local preparation; no extension or commit attempted'},null,2)+'\n');
const c=await connectRouter();try{await c.upload(d.localDir+'/cancel',d.stagePath+'/cancel');console.log(JSON.stringify({alreadyRestored:true,ownedStageCancellationRequested:true}));}finally{c.close()}
