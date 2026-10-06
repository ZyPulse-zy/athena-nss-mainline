import assert from 'node:assert/strict';
export const uint=n=>Number.isSafeInteger(n)&&n>=0&&n<=0xffffffff;
const ct=(key,dir)=>({ct:{key,...(dir?{dir}:{})}}),meta=key=>({meta:{key}}),pay=(protocol,field)=>({payload:{protocol,field}});
const match=(left,right,op='==')=>({match:{op,left,right}});
export function parseFlow(text,proto){
 const rows=text.split('\n').filter(x=>new RegExp('^(?:ipv4\\s+2\\s+)?'+proto+'\\s+').test(x));assert.equal(rows.length,1);
 const tuples=[...rows[0].matchAll(/src=(\S+) dst=(\S+) sport=(\d+) dport=(\d+)/g)].map(m=>({src:m[1],dst:m[2],sport:Number(m[3]),dport:Number(m[4])}));assert.equal(tuples.length,2);
 const id=Number(rows[0].match(/\bid=(\d+)/)?.[1]),mark=Number(rows[0].match(/\bmark=(\d+)/)?.[1]),wan=(mark&0xff0000)>>>16;
 assert.ok(uint(id)&&id>0&&uint(mark)&&wan>=1&&wan<=5&&!(mark&0x2000));
 assert.equal(tuples[0].src,'192.168.237.207');assert.equal(tuples[0].dst,tuples[1].src);assert.equal(tuples[0].dport,tuples[1].sport);
 return{protocol:proto==='udp'?17:6,zone:0,id,mark,wan,original:tuples[0],reply:tuples[1]};
}
export function buildPlan(flow,owner,mode='observe',ttlSeconds=35){
 assert.equal(flow.protocol,17);assert.match(owner,/^[a-f0-9]{32}$/);assert.ok(['observe','rt'].includes(mode));assert.ok(ttlSeconds>=20&&ttlSeconds<=45);
 const table='rp_nss15_'+owner.slice(0,16),objects=[{table:{family:'inet',name:table,comment:owner}}];
 const counter=()=>({counter:{packets:0,bytes:0}});
 const chain=(name,hook,prio)=>objects.push({chain:{family:'inet',table,name,type:'filter',hook,prio,policy:'accept'}});
 const rule=(chain,name,expr)=>objects.push({rule:{family:'inet',table,chain,comment:owner+':'+name,expr}});
 const guard=dir=>{
  const up=dir==='up';const e=[match(meta('nfproto'),2),match(meta('l4proto'),17),match(meta('iifname'),up?'br-lan':'rpwan'+flow.wan),match(meta('oifname'),up?'rpwan'+flow.wan:'br-lan'),match(ct('zone'),0),match(ct('direction'),up?0:1),match(ct('state'),2),match(ct('id'),flow.id),match(ct('mark'),flow.mark),match(ct('protocol'),17)];
  for(const [direction,t]of[['original',flow.original],['reply',flow.reply]])for(const[key,value]of[['ip saddr',t.src],['ip daddr',t.dst],['proto-src',t.sport],['proto-dst',t.dport]])e.push(match(ct(key,direction),value));
  return e;
 };
 if(mode==='rt'){
  chain('writer','forward',-150);
  for(const d of['up','down'])rule('writer','writer_'+d,[...guard(d),{mangle:{key:meta('priority'),value:d==='up'?0:0x8f060000}},counter()]);
 }
 for(const[stage,hook,priority]of[['forward','forward',-149],['post','postrouting',99]]){
  chain(stage,hook,priority);
  for(const d of['up','down']){
   const expected=mode==='rt'&&d==='down'?0x8f060000:0;
   rule(stage,stage+'_'+d+'_total',[...guard(d),counter()]);
   rule(stage,stage+'_'+d+'_expected',[...guard(d),match(meta('priority'),expected),counter()]);
   rule(stage,stage+'_'+d+'_unexpected',[...guard(d),match(meta('priority'),expected,'!='),counter()]);
  }
  const g=[match(meta('nfproto'),2),match(meta('l4proto'),17),match(pay('ip','saddr'),flow.original.src),match(pay('ip','daddr'),flow.original.dst),match(pay('udp','sport'),54374),match(pay('udp','dport'),flow.original.dport)];
  rule(stage,stage+'_neighbor_total',[...structuredClone(g),counter()]);
  rule(stage,stage+'_neighbor_zero',[...structuredClone(g),match(meta('priority'),0),counter()]);
  rule(stage,stage+'_neighbor_nonzero',[...structuredClone(g),match(meta('priority'),0,'!='),counter()]);
 }
 return{owner,table,mode,ttlSeconds,flow,expected:{nftables:objects},batch:{nftables:objects.map((o,i)=>({[i===0?'create':'add']:o}))},newNssPermit:false,newModule:false};
}
export function counters(native){return Object.fromEntries(native.nftables.filter(x=>x.rule).map(x=>x.rule).map(r=>[r.comment.split(':').at(-1),r.expr.find(x=>x.counter)?.counter]).filter(([,v])=>v));}
export function inspect(native,plan){
 const c=counters(native),directionChecks={};
 for(const stage of['forward','post'])for(const dir of['up','down']){
  const key=stage+'_'+dir,t=c[key+'_total'].packets,e=c[key+'_expected'].packets,u=c[key+'_unexpected'].packets;
  assert.equal(e+u,t);directionChecks[key]={total:t,expected:e,unexpected:u,nonzero:t>0,correct:u===0};
 }
 for(const stage of['forward','post']){
  const t=c[stage+'_neighbor_total'].packets,z=c[stage+'_neighbor_zero'].packets,n=c[stage+'_neighbor_nonzero'].packets;assert.equal(z+n,t);
 }
 return{mode:plan.mode,directionChecks,counters:c,allSelectedExpected:Object.values(directionChecks).every(x=>x.nonzero&&x.correct),neighborObserved:c.forward_neighbor_total.packets>0,neighborUnchanged:c.forward_neighbor_nonzero.packets===0&&c.post_neighbor_nonzero.packets===0,nssLeafProof:false,automaticClassification:false};
}
