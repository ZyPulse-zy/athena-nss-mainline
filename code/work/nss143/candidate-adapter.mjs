// The reader calls only A.new(...).candidates(). Keep those exact original
// checks and remove APIs that this visibility-only process never calls.
import assert from 'node:assert/strict';import {packLua} from '../nss140/pack-lua.mjs';
export function candidateAdapter(original){
 const at=s=>{const p=original.indexOf(s);assert.ok(p>=0&&original.indexOf(s,p+1)<0,'Non-unique original adapter boundary');return p;};
 const inspectEnd=at('function M.pair(s,c,now,selected)');
 const newBegin=at('function A.new(P,fs,j,read,now,run,record)');
 const contextEnd=at(' -- Hot readers perform the full inspection once, immediately before deciding.');
 const candidatesBegin=at(' function out.candidates()');
 const candidatesEnd=at(' function out.ready()');
 assert.ok(inspectEnd<newBegin&&newBegin<contextEnd&&contextEnd<candidatesBegin&&candidatesBegin<candidatesEnd);
 const exactInspect=original.slice(0,inspectEnd),exactContext=original.slice(newBegin,contextEnd),exactCandidates=original.slice(candidatesBegin,candidatesEnd);
 const source=exactInspect+'return M\nend)()\nlocal A={}\n'+exactContext+' local out={}\n'+exactCandidates+' return out\nend\nreturn A\n';
 assert.ok(source.includes('Consumer.inspect(s,c,now())')&&!source.includes('function out.ready')&&!source.includes('function M.pair'));
 return{source:packLua(source),retained:{exactInspect,exactContext,exactCandidates},removedApis:['pair','compareEpoch','ready','sample','renewal','retirement'],readonly:true,nssAdmissionAllowed:false};
}
