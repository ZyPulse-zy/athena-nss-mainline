// Reproduce the unchanged health controller's 300-bucket transition, not a
// blanket exception for routing drift. Does not permit NSS or mutate routing.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function proveWan4Failover(original,current,health){
 assert.equal(health.mode,'equal-per-connection');assert.equal(health.bucketCount,300);assert.deepEqual(health.weights,[100,100,100,0,100]);
 assert.deepEqual(health.wan.map(w=>w.healthy),[true,true,true,false,true]);
 const source=fs.readFileSync('work/nss109/health-controller.lua'),manifest=fs.readFileSync('work/nss108/protected-manifest-private.txt','utf8');
 assert.ok(manifest.includes(hash(source)+'  /root/router-project/scripts/health-controller.lua\n'));
 const rows=text=>{const result={};for(const m of text.matchAll(/(0x[0-9a-f]+) : jump mark_w([1-5])/g)){const key=Number(m[1]);assert.ok(!(key in result));result[key]=Number(m[2]);}assert.equal(Object.keys(result).length,300);assert.ok(Array.from({length:300},(_,i)=>i).every(i=>i in result));return result;};
 const oldMap=rows(original.pbr),newMap=rows(current.pbr),target=[75,75,75,0,75],retained=[0,0,0,0,0],free=[],expected={};
 for(let b=0;b<300;b++){const n=oldMap[b]-1;if(retained[n]<target[n]){expected[b]=n+1;retained[n]++;}else free.push(b);}
 for(const b of free){let best=0;for(let n=1;n<5;n++)if(target[n]-retained[n]>target[best]-retained[best])best=n;assert.ok(target[best]>retained[best]);expected[b]=best+1;retained[best]++;}
 assert.deepEqual(newMap,expected);assert.deepEqual(retained,target);assert.equal(free.length,60);
 const adapt=text=>{
  assert.deepEqual(rows(text),oldMap);text=text.replace(/(0x[0-9a-f]+) : jump mark_w([1-5])/g,(whole,slot)=>slot+' : jump mark_w'+expected[Number(slot)]);
  const healthy=[...text.matchAll(/\tset healthy \{[\s\S]*?\n\t\}/g)];assert.equal(healthy.length,1);const section=healthy[0][0];assert.equal(section.split('0x00040000, ').length,2);
  return text.replace(section,section.replace('0x00040000, ',''));
 };
 const pbrExpected=adapt(original.pbr),nftExpected=adapt(original.nftRuleset);
 // DNS dynamic-set normalization remains the original audit's responsibility.
 const currentRules=current.rules.split('\n');const removed=original.rules.split('\n').filter(x=>/ lookup 104$/.test(x)&&!currentRules.includes(x));assert.equal(removed.length,3);assert.deepEqual(removed.map(x=>Number(x.split(':')[0])),[10000,20000,90024]);
 const rulesExpected=original.rules.split('\n').filter(x=>!removed.includes(x)).join('\n');assert.equal(current.rules,rulesExpected);
 return{reference:{...original,pbr:pbrExpected,nftRuleset:nftExpected,rules:rulesExpected},proof:{passed:true,healthControllerSha256:hash(source),unchangedProtectedHealthControllerSource:true,currentAppliedWeights:health.weights,exact300BucketSourceAlgorithmReproduced:true,removedWan4Buckets:free.length,newBucketCounts:retained,healthySetOnlyWan4Removed:true,onlyThreeWan4DhcpRulesRemoved:true,experimentRoutingMutation:false,nssPermissionGranted:false}};
}
