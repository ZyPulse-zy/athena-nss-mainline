"""Merge verified single-CI retirement into the equal-window final client test."""
from pathlib import Path
import json
w=Path(__file__).resolve().parents[2];r=w/'work/nss140';r.mkdir(exist_ok=True)
for name in ['classifier.lua','qos-physical.lua','tag-normalizer.lua','module-stage.mjs','module-stage-guardian.lua','payload.mjs','pack-lua.mjs','pack-guardian.mjs','compact-default-queues.mjs','uplink-tag-plan.mjs','parse-ecm-any-wan.mjs','failed-wan-owner.lua','declared-baseline.mjs','service-epoch.mjs','current-audit-diagnostic.mjs']:
 b=(w/'work/nss138'/name).read_bytes();s=b.replace(b'nss138',b'nss140').replace(b'NSS138',b'NSS140');assert s.replace(b'nss140',b'nss138').replace(b'NSS140',b'NSS138')==b
 if name=='current-audit-diagnostic.mjs':
  old=b'controlled-class-';assert s.count(old)==1;s=s.replace(old,b'real-matched-aba-')
 (r/name).write_bytes(s)
for name in ['qos-native-qualification.json','normalizer-qualification.json','uplink-capacity-private.json']:(r/name).write_bytes((w/'work/nss138'/name).read_bytes())
old=(w/'work/nss128/fast-path.lua').read_text(encoding='utf-8');s=(w/'work/nss138/fast-path.lua').read_text(encoding='utf-8')
def part(text,a,b):return text[text.index(a):text.index(b,text.index(a))]
def replace(a,b):
 global s
 assert s.count(a)==1,a[:80];s=s.replace(a,b)
replace('local out={};local session;local tagBase','local out={};local session;local tagBase;local active=false;local retire')
replace('local r={uptime=now(),stop4=tonumber(read(\'/sys/kernel/debug/ecm/front_end_ipv4_stop\',128)),stop6=tonumber(read(\'/sys/kernel/debug/ecm/front_end_ipv6_stop\',128)),counts={}}','local r={uptime=now(),stop4=tonumber(read(\'/sys/kernel/debug/ecm/front_end_ipv4_stop\',128)),stop6=tonumber(read(\'/sys/kernel/debug/ecm/front_end_ipv6_stop\',128)),counts={},cpu=read(\'/proc/stat\',16384),softnet=read(\'/proc/net/softnet_stat\',16384),interfaces={}}')
anchor="  assert(r.stop6==1 and r.counts['ecm_nss_ipv6/accelerated_count']==0"
line=next(x for x in old.splitlines()if "for _,d in ipairs({'rpwan1'"in x)
assert s.count(anchor)==1;s=s.replace(anchor,line+'\n'+anchor)
replace("  assert(comparison.action=='KEEP_IMMUTABLE_EPOCH','Class or exact instance changed')\n  return{sequence=frame.sourceSequence}","  if comparison.action~='KEEP_IMMUTABLE_EPOCH'then\n   if active then retire(comparison)end\n   error('CLASS_OR_INSTANCE_CHANGED_REQUIRES_NEW_CHECKPOINT_AND_EPOCH',0)\n  end\n  return{sequence=frame.sourceSequence,producer=frame.producer,queryStarted=frame.startedAtUptime,queryAge=now()-frame.startedAtUptime}")
retire=part(s,'   assert(changed);record.parametersBeforeSingleRetire=parameters()',"  end\n  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\\n');record.frontendClosedAt")
retire=retire.replace('   assert(changed);','   ')
retire=" retire=function(comparison)\n  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','1\\n');record.reclassificationFrontendStoppedAt=now()\n  M.verifyReclassification(comparison,record.adapterProducer);record.actualReclassification=comparison\n"+retire+"  record.classTransitionHandled=true;record.requiresFreshEpoch=true\n end\n"
measure=part(old,' local function tick(name)',' function out.align(deadline)')
assert s.count(' function out.align(deadline)')==1;s=s.replace(' function out.align(deadline)',retire+measure+' function out.align(deadline)')
tail=part(old,"  record.qosAtA=qos.snapshot();measure('A');checkedTags('tagsAfterA',live)",' return out\nend\nreturn M')
tail=tail.replace(';loaded=true;stopped()', ';stopped()').replace(';loaded=false;stopped()', ';active=false;stopped()')
tail=tail.replace("  put('/sys/kernel/debug/ecm/front_end_ipv4_stop','0\\n');", "  active=true;put('/sys/kernel/debug/ecm/front_end_ipv4_stop','0\\n');")
a=s.index("  record.samples[#record.samples+1]=sample();checkedTags('tagsAfterA',live)");b=s.index(' return out\nend\nreturn M',a);s=s[:a]+tail+s[b:]
replace('record.classLifecycleVersion=129;record.samples={};record.renewals={};','record.abaVersion=140;record.phases={};record.samples={};record.renewals={};')
assert 'P.relearnOnly'not in s and 'local waitUntil=math.min(now()+16'not in s
(r/'fast-path.lua').write_text(s,encoding='utf-8')
print(json.dumps({'prepared':True,'productionWrites':False,'equalPhaseSeconds':20,'sourceMaximumSeconds':6,'nativeMaximumSeconds':27,'ownerMaximumSeconds':100,'nativeRetirementBodyInheritedFrom138':True,'newHumanExperimentExecuted':False}))
