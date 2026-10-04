// Offline timestamp mapping of already archived, actual Sky captures.
// Phase assignment does not certify screenshot content or invent HUD metrics.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const dir=process.argv[2];assert.match(dir,/^work\/nss(?:49|50)\/real-matched-aba-\d+-[a-f0-9]+$/);
const labels=process.argv.slice(3);assert.equal(labels.length,2);for(const x of labels)assert.match(x,/^[a-z0-9-]+$/);
const anchors=labels.map(x=>JSON.parse(fs.readFileSync('work/nss50/clock-'+x+'-private.json')));
const offsets=anchors.map(a=>(a.localRequestMs+a.localReceiptMs)/2-a.routerUptime*1000);
const uncertaintyMs=Math.max(...anchors.map(a=>a.roundTripMs/2))+20;
const lowerOffset=Math.min(...offsets)-uncertaintyMs,upperOffset=Math.max(...offsets)+uncertaintyMs;
const r=JSON.parse(fs.readFileSync(dir+'/last-record-private.json'));assert.ok(r.phases?.length>0);
const out={case:dir,clockAnchorLabels:labels,clockOffsetDriftMs:Math.abs(offsets[1]-offsets[0]),uncertaintyMs,missingHudNeverZero:true,humanGameplay:false,phaseMaps:r.phases.map(p=>({phase:p.name,startedAtUptime:p.startedAt,endedAtUptime:p.endedAt,completed:p.completed===true,frames:[]}))};
for(const name of fs.readdirSync('work/nss50')){
 if(!/^hud-\d+-private$/.test(name)||!fs.existsSync('work/nss50/'+name+'/completion.json'))continue;
 const completion=JSON.parse(fs.readFileSync('work/nss50/'+name+'/completion.json'));
 const frames=JSON.parse(fs.readFileSync('work/nss50/'+name+'/frames.json'));assert.equal(frames.length,completion.frames);
 for(const f of frames){
  assert.match(f.file,/^\d{3}\.jpg$/);assert.equal(f.source,'Actual Sky window capture');
  const min=(Date.parse(f.beforeAt)-upperOffset)/1000,max=(Date.parse(f.afterAt)-lowerOffset)/1000;
  assert.ok(Number.isFinite(min)&&Number.isFinite(max)&&max>=min);
  for(const p of out.phaseMaps){
   if(min>=p.startedAtUptime&&max<=p.endedAtUptime){
    const file='work/nss50/'+name+'/'+f.file;
    p.frames.push({...f,file,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),uptimeMinimum:min,uptimeMaximum:max,atLeastOneSecondFromBothPhaseBoundaries:min>=p.startedAtUptime+1&&max<=p.endedAtUptime-1,visualContentVerified:false,usableUntilVisualVerification:false});
   }
  }
 }
}
const path='work/nss50/client-map-'+dir.split('/').at(-1)+'-private.json';
fs.writeFileSync(path,JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({output:path,clockOffsetDriftMs:out.clockOffsetDriftMs,uncertaintyMs,phases:out.phaseMaps.map(p=>({phase:p.phase,mappedFrames:p.frames.length,centralFrames:p.frames.filter(f=>f.atLeastOneSecondFromBothPhaseBoundaries).length})),contentStillRequiresVisualReview:true}));
