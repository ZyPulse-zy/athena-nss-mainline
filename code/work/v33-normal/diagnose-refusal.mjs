import fs from'node:fs';import assert from'node:assert/strict';import{canonicalSelection}from'../nss27/flow-selection.mjs';import{selectAnchoredTriple}from'./normal-selection.mjs';
const root='work/v33-normal',cases=fs.readdirSync(root).filter(n=>/^session-\d+-[a-f0-9]+$/.test(n)&&fs.existsSync(root+'/'+n+'/controller-error.json'));assert.equal(cases.length,1);
const dir=root+'/'+cases[0],read=p=>JSON.parse(fs.readFileSync(p)),selected=read(dir+'/persistent-selection-private.json').selected,frame=read(root+'/controlled-candidates-private.json');
assert.equal(read(dir+'/controller-error.json').error,'AssertionError [ERR_ASSERTION]: Exact controlled socket pair changed before staging');
for(const name of['controlled-candidates-private.json','controlled-pc-raw-private.json','normal-reader-process-private.json','pc-app-endpoints-private.json','real-candidates-private.json','real-candidates-raw-private.json','real-reader-qualified.json'])fs.copyFileSync(root+'/'+name,dir+'/refusal-'+name,fs.constants.COPYFILE_EXCL);
const present={};for(const[slot,list]of[['tcp',frame.tcp],['udp',frame.udp],['tcp2',frame.tcp]])present[slot]=list.some(f=>JSON.stringify(canonicalSelection(f))===JSON.stringify(selected[slot]));
const alternatives=selectAnchoredTriple(frame,selected.udp,{tcp:selected.tcp.wan,tcp2:selected.tcp2.wan});
const out={passed:true,diagnosticOnly:true,originalRefusalPreserved:true,observedAt:new Date().toISOString(),controllerCase:dir,selectedStillEligible:present,
 actualGameCandidates:frame.udp.length,actualBulkCandidates:frame.tcp.length,sameWanOriginalGameAlternatives:alternatives.length,
 originalGameAndWanSlotsCouldBeRetained:alternatives.length>0,checkpointCreated:fs.existsSync(dir+'/stage-checkpoint-private.json'),detachedStageStarted:fs.existsSync(dir+'/stage-receipt-private.json'),
 nssStarted:false,missingCandidateDoesNotProveCtExit:true,rootCauseBeyondEligibilityEstablished:false};
fs.writeFileSync(root+'/refusal-diagnosis.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
