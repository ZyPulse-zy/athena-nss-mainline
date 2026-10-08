import assert from 'node:assert/strict';

// The first classifier read discovers only which ports to inspect. It cannot
// authorize admission after the OS query. Admission uses a separate final read.
export async function collectFreshOwnedFrame({readNative,readPc,clock}){
 const discoveryBegan=clock.monotonic();
 const discovery=await readNative('discovery');
 assert.equal(discovery.routerWrites,false);assert.equal(discovery.nssAdmissionAllowed,false);
 assert.ok(Array.isArray(discovery.flows)&&discovery.flows.length<=128);
 if(!discovery.flows.length){
  const elapsed=(clock.monotonic()-discoveryBegan)/1000;assert.ok(Number.isFinite(elapsed)&&elapsed>=0);
  discovery.sourceAge+=elapsed;
  assert.ok(Number.isFinite(discovery.sourceAge)&&discovery.sourceAge>=0&&discovery.sourceAge<6,'Empty classifier source expired');
  return {native:discovery,pc:{at:new Date(clock.wall()).toISOString(),ageSeconds:0,processes:[],tcp:[],udp:[]},discoveryOnlyEmpty:true};
 }
 const requested=new Set(discovery.flows.map(f=>f.identity.original.sport));
 const pc=await readPc(discovery.flows);
 const began=clock.monotonic(),native=await readNative('final');
 assert.equal(native.routerWrites,false);assert.equal(native.nssAdmissionAllowed,false);
 assert.equal(native.producer,discovery.producer,'Classifier owner changed during socket discovery');
 assert.ok(Number.isSafeInteger(native.sourceSequence)&&native.sourceSequence>=discovery.sourceSequence,'Classifier query regressed');
 const readSeconds=(clock.monotonic()-began)/1000;assert.ok(Number.isFinite(readSeconds)&&readSeconds>=0);
 // Conservatively include the entire FINAL remote read, never discard its
 // network time. OS freshness includes its own query and the final remote read.
 native.sourceAge+=readSeconds;
 pc.ageSeconds=(clock.wall()-Date.parse(pc.at))/1000;
 assert.ok(Number.isFinite(native.sourceAge)&&native.sourceAge>=0&&native.sourceAge<6,'Final classifier source expired');
 assert.ok(Number.isFinite(pc.ageSeconds)&&pc.ageSeconds>=0&&pc.ageSeconds<6,'OS socket source expired');
 native.flows=native.flows.filter(f=>requested.has(f.identity.original.sport));
 return {native,pc,discoveryOnlyEmpty:false};
}
