// Preserve actual post-checkpoint input and reduce the final admission failure locally.
// No extra router query, instrumentation, or production retry is authorized here.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root='work/v34-normal';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const cases=fs.readdirSync(root).filter(n=>/^session-\d+-[a-f0-9]+$/.test(n)&&fs.existsSync(root+'/'+n+'/controller-error.json'));
assert.equal(cases.length,1);
const dir=root+'/'+cases[0],record=read(dir+'/last-record-private.json');
const selected=read(dir+'/selected-private.json');
const frame=read(root+'/controlled-candidates-private.json');
const finalSelection=read(dir+'/post-checkpoint-selection-receipt.json');
assert.ok(finalSelection.passed);
assert.match(read(dir+'/controller-error.json').error,/Initial admission refused:.*Selected class is not admitted/s);
assert.equal(record.newNssPermit,false);assert.equal(record.gateComplete,false);
assert.equal(record.moduleLoaded,false);assert.equal(record.initialAlignment.probes.length,1);
assert.equal(record.initialAlignment.probes[0][1],false);
const files=['controlled-candidates-private.json','controlled-pc-raw-private.json','normal-reader-process-private.json','pc-app-endpoints-private.json','real-candidates-private.json','real-candidates-raw-private.json','real-reader-qualified.json'];
const copies={};
for(const name of files){
 const data=fs.readFileSync(root+'/'+name);assert.ok(data.length<=1048576);
 const target=dir+'/last-post-checkpoint-'+name;
 fs.copyFileSync(root+'/'+name,target,fs.constants.COPYFILE_EXCL);
 assert.deepEqual(fs.readFileSync(target),data);
 copies[name]=crypto.createHash('sha256').update(data).digest('hex');
}
const key=f=>[f.wan,f.mark,f.protocol===6?'tcp':'udp',f.original.src,f.original.sport,f.reply.src,f.reply.dst,f.reply.sport,f.reply.dport,f.zone,f.id].join('|');
const byKey=new Map([...frame.bulk,...frame.game].map(f=>[f.key,f]));
const lastSelectedClasses={};
for(const slot of ['tcp','udp','tcp2'])lastSelectedClasses[slot]=byKey.get(key(selected[slot]))?.decision.class??null;
assert.deepEqual(lastSelectedClasses,{tcp:'BULK',udp:'RT',tcp2:'BULK'});
const out={passed:true,localExistingInputsOnly:true,networkReads:0,routerWrites:0,
 originalAdmissionFailurePreserved:true,oneControllerAttemptOnly:true,
 loadBeforeController:{actualCs2Rt:1,actualSteamBulk:11,eligibleMultiWanTriples:1},
 preparedNativeWanCount:fs.readdirSync(dir).filter(n=>/^prepared-prerequisites-wan-[1-5]-private\.json$/.test(n)).length,
 initialWanFreezeAfterNativePreparationPassed:read(dir+'/final-selection-before-wan-freeze-private.json').passed,
 postCheckpointSelectionPassed:finalSelection.passed,
 lastPostCheckpointSelectedClasses:lastSelectedClasses,
 lastPostCheckpointSequence:frame.sourceSequence,
 initialOwnerProbeCount:1,initialOwnerProbeSucceeded:false,
 initialOwnerRejection:'Selected class is not admitted',
 initialOwnerFullClassifierSnapshotCaptured:false,
 classifierSnapshotRecords:record.classifierSnapshots.length,
 exactAbsentSlotAndClassChangeCauseEstablished:false,
 missingCandidateDoesNotProveCtExit:true,firmwareFaultEstablished:false,
 checkpointCreated:true,checkpointDownloadedShaAndGzipVerified:read(dir+'/stage-checkpoint-verified.json').gzipVerified,
 detachedStageStarted:true,independentUndoBeforeFirstWrite:read(dir+'/stage-receipt-private.json').rollbackBeforeFirstWrite,
 selectedWanSet:[...new Set(Object.values(selected).map(f=>f.wan))].sort(),
 nssGateModuleLoaded:false,ecmPermitGranted:false,fastPathMeasurementStarted:false,
 wholeFactoryAcceptance:false,installedGateRetargeted:false,
 stageUndoVerified:read(dir+'/stage-undo-verified.json'),
 lastPostCheckpointInputCopiesExact:files.length,
 privateInputSha256:copies,observedAt:new Date().toISOString()};
assert.equal(out.classifierSnapshotRecords,0);assert.equal(out.preparedNativeWanCount,5);
fs.writeFileSync(root+'/admission-diagnosis.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...out,privateInputSha256:undefined}));
