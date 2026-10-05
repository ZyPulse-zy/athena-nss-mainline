import fs from 'node:fs';import zlib from'node:zlib';import{packGuardian}from'./pack-guardian.mjs';import{encode}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const source=fs.readFileSync('work/nss137/module-stage-guardian.lua','utf8'),plan=JSON.parse(fs.readFileSync('work/nss135/controlled-class-20261005220728-a0f315c4/stage-plan-private.json'));
for(const k of ['guardianSourceSha256','selectedGuardianSha256','oneEpochControlledPair','phaseSourceSha256','qosSourceSha256','execBytes'])delete plan[k];
const loop="for _,key in ipairs({'moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'})do assert(record[key]==true,'Success teardown incomplete: '..key)end";
const keys=['moduleUnloaded','tagsRemoved','qosRestored','qosModuleUnloaded','dualPhysicalQueuesRestored','wanRestored','mwan3Restored','stateNodeRemoved'];
for(const [name,s]of Object.entries({original:source,noMessage:source.replace(loop,loop.replace(",'Success teardown incomplete: '..key",'')),combined:source.replace(loop,'assert('+keys.map(k=>'record.'+k+'==true').join(' and ')+')')})){
 const text="/usr/bin/lua - <<'NSS20_STAGE_BEGIN'\n"+packGuardian(s).replace('__PLAN__',()=>JSON.stringify(plan)).replace('__CORE_PHASE__',()=> 'return{}').replace('__QOS_PHYSICAL__',()=> 'return{}')+"\nNSS20_STAGE_BEGIN\n";let result;try{const e=encode(text);result={execBytes:e.execBytes}}catch(e){result={error:String(e)}}
 console.log(JSON.stringify({name,rawBytes:Buffer.byteLength(text),gzipSourceBytes:zlib.gzipSync(text,{level:9}).length,...result}));
}
