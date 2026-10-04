import fs from 'node:fs';import assert from 'node:assert/strict';
import {adoptServices,verifyEpochServices} from './service-epoch.mjs';
const historical={'sing-box-athena':{core:{pid:301,running:true,command:['/usr/bin/sing-box','run','-c','/authorized/config.json']},guard:{pid:302,running:true,command:['/bin/sh','/authorized/guard.sh']}},'router-project-game-classifier':{classifier:{pid:401,running:true,command:['/usr/bin/lua','/authorized/worker.lua']},guardian:{pid:402,running:true,command:['/usr/bin/lua','/authorized/guardian.lua']}},minieap:{wan1:{pid:501,running:true,command:['/usr/bin/minieap','-i','rpwan1']}}};
const current=structuredClone(historical);current['sing-box-athena'].core.pid=601;current['sing-box-athena'].guard.pid=602;
const results=[];
function check(name,fn){fn();results.push({name,passed:true});}
check('historical-identities-unchanged',()=>assert.deepEqual(adoptServices(historical,historical).changes,[]));
check('healthy-preexisting-two-pid-change',()=>assert.equal(adoptServices(historical,current).changes.length,2));
for(const [name,mutate] of [
 ['core-command',x=>x['sing-box-athena'].core.command.push('--new')],
 ['guard-command',x=>x['sing-box-athena'].guard.command.push('--new')],
 ['core-stopped',x=>x['sing-box-athena'].core.running=false],
 ['guard-stopped',x=>x['sing-box-athena'].guard.running=false],
 ['missing-instance',x=>delete x['sing-box-athena'].guard],
 ['added-instance',x=>x['sing-box-athena'].unknown={pid:603,running:true,command:[]}],
 ['missing-service',x=>delete x.minieap],
 ['added-service',x=>x.unknown={main:{pid:604,running:true,command:[]}}],
 ['unrelated-pid',x=>x.minieap.wan1.pid=999],
 ['unrelated-stopped',x=>x.minieap.wan1.running=false],
 ['unrelated-command',x=>x.minieap.wan1.command.push('--new')],
 ['zero-pid',x=>x['sing-box-athena'].core.pid=0],
 ['fractional-pid',x=>x['sing-box-athena'].core.pid=601.5],
 ['negative-pid',x=>x['sing-box-athena'].guard.pid=-1],
 ['unexpected-instance-field',x=>x['sing-box-athena'].core.unknown=true]
])check('adoption-rejects-'+name,()=>{const x=structuredClone(current);mutate(x);assert.throws(()=>adoptServices(historical,x));});
check('epoch-retains-exact-services',()=>assert.equal(verifyEpochServices(current,current),true));
for(const [name,mutate] of [
 ['core-pid',x=>x['sing-box-athena'].core.pid++],
 ['guard-pid',x=>x['sing-box-athena'].guard.pid++],
 ['core-command',x=>x['sing-box-athena'].core.command.push('--new')],
 ['guard-stopped',x=>x['sing-box-athena'].guard.running=false],
 ['unrelated-pid',x=>x.minieap.wan1.pid++],
 ['unknown-service',x=>x.unknown={}]
])check('within-epoch-rejects-'+name,()=>{const x=structuredClone(current);mutate(x);assert.throws(()=>verifyEpochServices(current,x));});
const out={passed:true,cases:results.length,results,syntheticServiceFixtures:true,noRouterOrServiceWrites:true,nssPermissionGranted:false,withinExperimentServiceDriftRejected:true};
fs.writeFileSync('work/nss50/service-epoch-tests.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({passed:true,cases:results.length,noRouterOrServiceWrites:true}));
