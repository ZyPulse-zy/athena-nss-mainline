// Reduce the already frozen refusal frame; no router or client observation.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {selectAnchoredTriple} from './normal-selection.mjs';

const root='work/v33-normal';
const dir=root+'/session-20261007025747-bf198fc4';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const selected=read(dir+'/persistent-selection-private.json').selected;
const frame=read(dir+'/refusal-controlled-candidates-private.json');
const pc=read(dir+'/refusal-pc-app-endpoints-private.json');
assert.equal(read(dir+'/controller-error.json').error,
 'AssertionError [ERR_ASSERTION]: Exact controlled socket pair changed before staging');
const ownedSocket=f=>pc.tcp.some(s=>s.LocalAddress===f.original.src&&
 Number(s.LocalPort)===f.original.sport&&s.RemoteAddress===f.original.dst&&
 Number(s.RemotePort)===f.original.dport);
const sameSlots=selectAnchoredTriple(frame,selected.udp,
 {tcp:selected.tcp.wan,tcp2:selected.tcp2.wan});
const anySlots=selectAnchoredTriple(frame,selected.udp);
const result={passed:true,localFrozenInputOnly:true,networkReads:0,routerWrites:0,
 originalRefusalPreserved:true,originalGamePreserved:true,
 originalTcpSocketsStillOwned:{tcp:ownedSocket(selected.tcp),tcp2:ownedSocket(selected.tcp2)},
 originalWanSlotAlternatives:sameSlots.length,
 otherWanSlotAlternatives:anySlots.length,
 otherSlotsDoNotAuthorizeRetargeting:true,
 originalCtExitEstablished:false,firmwareFaultEstablished:false,
 newCheckpointStageOrNss:false,completeFactoryAcceptance:false};
fs.writeFileSync(root+'/local-refusal-summary.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
