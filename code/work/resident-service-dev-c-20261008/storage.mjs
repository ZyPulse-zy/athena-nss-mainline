import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {servicePlan} from './policy.mjs';
export const serviceRoot='work/resident-service-dev-c-20261008';
export const runPattern=/^work\/resident-service-run-\d{14}-[a-f0-9]{8}$/;
export const observerPattern=/^work\/resident-normal-observe-\d{14}-[a-f0-9]{8}$/;
const recordPattern=/^normal-(native|pc|frame)-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-private\.json$/;
export const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
export const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
export const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
export function atomic(p,v){const t=p+'.'+crypto.randomUUID()+'.tmp';save(t,v);fs.renameSync(t,p);}
export function createObserver(owner){
 assert.match(owner,runPattern);
 const root='work/resident-normal-observe-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');
 fs.mkdirSync(root);save(root+'/resident-service-owner-private.json',{owner,operationalObservationBuffer:true,retainedGroups:servicePlan.retainedObservationGroups});return root;
}
// Only new operational observation records belonging to this service are rotated.
// Hardware generations, failures and all historical/frozen evidence are untouched.
export function rotateObserver(root,owner){
 assert.match(root,observerPattern);assert.match(owner,runPattern);
 const marker=read(root+'/resident-service-owner-private.json');assert.equal(marker.owner,owner);assert.equal(marker.operationalObservationBuffer,true);
 const groups=new Map();
 for(const name of fs.readdirSync(root))if(recordPattern.test(name)){
  const p=path.join(root,name),s=fs.lstatSync(p);assert.ok(s.isFile()&&!s.isSymbolicLink());
  const token=name.match(/^normal-(?:native|pc|frame)-(.+)-private\.json$/)[1];const g=groups.get(token)??{time:0,names:[]};g.time=Math.max(g.time,s.mtimeMs);g.names.push(name);groups.set(token,g);
 }
 const oldest=[...groups.values()].sort((a,b)=>a.time-b.time).slice(0,Math.max(0,groups.size-servicePlan.retainedObservationGroups));
 for(const g of oldest)for(const name of g.names){const target=path.resolve(root,name);assert.equal(path.dirname(target),path.resolve(root));fs.unlinkSync(target);}
 return{groupsRetained:Math.min(groups.size,servicePlan.retainedObservationGroups),groupsPruned:oldest.length};
}
