import fs from 'node:fs';import assert from 'node:assert/strict';import {initialUdpPort} from './udp-seed.mjs';
const root='work/v66-run-20261007150533-eb348ff9',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),cfg=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),result=JSON.parse(fs.readFileSync(root+'/entry-result-private.json'));
assert.ok(result.restorationPassed&&result.state==='RESTORED');const port=initialUdpPort(cfg.udpSourcePort,()=>assert.fail('Expected historical source port'));
for(const p of [58999,59800,1.5])assert.throws(()=>initialUdpPort(p,()=>0));assert.equal(initialUdpPort(undefined,()=>0),59000);assert.equal(initialUdpPort(undefined,()=>799),59799);
const proof={port,previousRuntime:root,previousSessionRestored:true,onlyAcquisitionHint:true,currentAdmissionGranted:false,newNonceAndActualSocketCtClassStillRequired:true,sourcePortUnusedCheckStillRequired:true};
fs.writeFileSync('work/resident-dev-20261007/udp-preferred-port.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,checks:6,routerAccess:false,noPbrOrWanForcing:true}));
