import assert from 'node:assert/strict';
import {candidateAdapter} from '../nss143/candidate-adapter.mjs';
import {packLua} from '../nss140/pack-lua.mjs';
export const fullFrameMethod=String.raw`
 function out.ownedFullFrame(expected,owned)
  local ok,result=pcall(function()
   local s,c=readContext();local checked=Consumer.inspect(s,c,now())
   if checked.producer~=expected.producer or checked.provenance.sequence~=expected.sourceSequence then return{status='QUERY_CHANGED',nssAdmissionAllowed=false}end
   local full=assert(j.parse(stable(ram..'/snapshot.json',4194304)))
   if full.producer~=checked.producer or not Consumer.sameProvenance(full.snapshot and full.snapshot.provenance,checked.provenance)then return{status='FULL_QUERY_UNAVAILABLE',nssAdmissionAllowed=false}end
   local complete=Consumer.inspect(full,c,now())
   local byKey={};for _,f in ipairs(complete.candidates)do byKey[f.key]=f end
   local count=0;for _ in pairs(byKey)do count=count+1 end;assert(count==#checked.candidates,'Projection candidate count disagreement')
   for _,f in ipairs(checked.candidates)do local other=assert(byKey[f.key],'Projection candidate absent in full query');assert(Consumer.sameProvenance(f.identity,other.identity)and Consumer.sameProvenance(f.decision,other.decision)and Consumer.sameProvenance(f.leaf,other.leaf),'Projection candidate fields disagreement')end
   local ports={};for _,p in ipairs(owned.tcpPorts)do assert(type(p)=='number'and p==math.floor(p)and p>0 and p<65536);ports[p]=true end
   local flows={};for _,f in ipairs(full.snapshot.flows)do local i=f.identity;local o=i.original
    if o.src==owned.clientAddress and((i.protocolNumber==6 and o.dst==owned.tcpServerAddress and o.dport==22 and ports[o.sport])or(i.protocolNumber==17 and o.dst==owned.udpServerAddress and o.sport==owned.udpSourcePort and o.dport==owned.udpPort))then flows[#flows+1]=f end
   end
   assert(#flows<=5,'Owned full frame exceeds fixed five sockets')
   return{status='SAME_QUERY_COMPLETE',producer=complete.producer,provenance=complete.provenance,flows=flows,projectionCandidatesPreserved=true,nssAdmissionAllowed=false}
  end)
  if ok then return result end
  return{status='FULL_FRAME_REFUSED',error=tostring(result),nssAdmissionAllowed=false}
 end
`;
export function fullCandidateAdapter(original){
 const kept=candidateAdapter(original).retained;
 const inspect=kept.exactInspect+'M.sameProvenance=equal\nreturn M\nend)()\nlocal A={}\n';
 const source=inspect+kept.exactContext+' local out={}\n'+kept.exactCandidates+fullFrameMethod+' return out\nend\nreturn A\n';
 assert.ok(source.includes(kept.exactInspect)&&source.includes(kept.exactContext)&&source.includes(kept.exactCandidates));
 return{source:packLua(source),originalAdmissionUnchanged:true,diagnosticOnly:true,nssAdmissionAllowed:false};
}
export function patchFullReader(source){
 const once=(before,after)=>{assert.equal(source.split(before).length,2,before);source=source.replace(before,after);};
 once("import{candidateAdapter}from'../nss143/candidate-adapter.mjs';","import{fullCandidateAdapter as candidateAdapter}from'../resident-dev-20261007/full-classification.mjs';");
 source="import{createClassificationFrameWriter}from'../resident-dev-20261007/record-classification.mjs';\n"+source;
 once('let readerConnection;','const writeClassificationFrame=createClassificationFrameWriter();let readerConnection;');
 once('local candidates=a.candidates();local flows={};',"local candidates=a.candidates();local fullFrame=a.ownedFullFrame(candidates,assert(j.parse([===[${JSON.stringify({clientAddress:config.clientAddress,tcpServerAddress:config.tcpServerAddress,udpServerAddress:config.serverAddress,tcpPorts:routePorts,udpSourcePort:status.udpSourcePort,udpPort:config.udpPort})}]===])));local flows={};");
 once('print(j.stringify({ownedTransportRoutes=routes','print(j.stringify({ownedFullFrame=fullFrame,ownedTransportRoutes=routes');
 once("fs.writeFileSync(root+'/controlled-candidates-private.json',JSON.stringify(out,null,2)+'\\n');", "writeClassificationFrame(root,out);");
 once('sourceAge:native.sourceAge,actualPermanentClassifierUsed:true',"sourceAge:native.sourceAge,fullFrameStatus:native.ownedFullFrame?.status,ownedClasses:native.ownedFullFrame?.status==='SAME_QUERY_COMPLETE'?native.ownedFullFrame.flows.map(f=>({wan:f.identity.wan,protocol:f.identity.protocolNumber,class:f.decision.class,reason:f.decision.reason,rateKbps:f.decision.rateKbps})):undefined,actualPermanentClassifierUsed:true");
 return source;
}
