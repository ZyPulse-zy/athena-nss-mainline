import assert from 'node:assert/strict';
export const residentTrial=Object.freeze({phaseSeconds:90,kernelHardSeconds:120,ownerSeconds:180,cleanupMarginSeconds:35,clientMinimumRemainingSeconds:160});
export function patchResidentWindow(source){
 const changes=[['R.deadline-95','R.deadline-125'],['requestedSeconds=60','requestedSeconds=90'],['s.uptime-start>=60','s.uptime-start>=90'],['p.seconds>=60 and p.seconds<=61.5','p.seconds>=90 and p.seconds<=91.5'],['now()+90,R.deadline-28','now()+120,R.deadline-28'],['N/1000-now()>=89','N/1000-now()>=119'],['minimumStableSeconds=60','minimumStableSeconds=90']];
 for(const [before,after] of changes){assert.equal(source.split(before).length,2,before);source=source.replace(before,after);}
 return source;
}
export function residentSchedule(ownerElapsed,clientRemaining){
 assert.ok(Number.isFinite(ownerElapsed)&&ownerElapsed>=0&&Number.isFinite(clientRemaining));
 return {allowed:ownerElapsed<=32&&clientRemaining>=residentTrial.clientMinimumRemainingSeconds,
  nativeHardSeconds:Math.min(residentTrial.kernelHardSeconds,residentTrial.ownerSeconds-ownerElapsed-28),
  fixedOwnerSeconds:residentTrial.ownerSeconds,permanentNssDeployment:false,procdRestartPolicyChanged:false};
}
