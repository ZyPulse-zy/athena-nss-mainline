from pathlib import Path
import json
p=Path('work/nss129/fast-path.lua');s=p.read_text()
old="return{sequence=frame.sourceSequence,producer=frame.producer,queryStarted=frame.startedAtUptime,queryAge=now()-frame.startedAtUptime,checkSeconds=now()-began}"
assert s.count(old)==1;s=s.replace(old,'return{sequence=frame.sourceSequence}')
old="record.tagCounterRereads=record.tagCounterRereads or{};record.tagCounterRereads[#record.tagCounterRereads+1]={key=key,reads=1,nssAdmissionAllowed=false,contract='monotonic-overlap-zero-wrong-tag'}"
assert s.count(old)==1;s=s.replace(old,"record.tagCounterReread=true")
a=s.index('   record.initialAlignment.diagnostics=');b=s.index('   record.lastAdmissionProbe=nil',a);s=s[:a]+s[b:]
old='local iterationStarted=now();stopped();local phaseStarted=now();phase.scan(fs,read,P.coreGuard);local phaseDone=now()';assert s.count(old)==1;s=s.replace(old,'stopped();phase.scan(fs,read,P.coreGuard)')
old="record.abaVersion=32;record.phases={};";assert s.count(old)==1;s=s.replace(old,'record.classLifecycleVersion=129;')
old="record.initialTagReadiness={startedAt=now(),deadline=getterUntil,probes=0,maximumWaitSeconds=1.2}";assert s.count(old)==1;s=s.replace(old,'record.initialTagWaitSeconds=1.2')
old="record.tagMeasurementEpoch={baselineAt=now(),warmupSeconds=0.1,contract='absolute-raw-retained-zero-new-wrong-tag',baselineCounters=j.parse(j.stringify(tagBase)),nssAdmissionAllowed=false}";assert s.count(old)==1;s=s.replace(old,'record.tagEpochBaselineAt=now()')
old='   record.initialTagReadiness.probes=record.initialTagReadiness.probes+1\n';assert s.count(old)==1;s=s.replace(old,'')
old='if not pending then record.initialTagReadiness.completedAt=now();break end';assert s.count(old)==1;s=s.replace(old,'if not pending then break end')
for before,after in [('No joint fresh classifier/core phase with room for B and A2','Fresh classifier/core phase unavailable'),('Insufficient fresh-classifier margin for complete ABA','Classifier setup margin unavailable'),('Native session lacks ABA retirement margin','Native session margin unavailable'),('Complete real reclassification unavailable within original lease','Complete class change unavailable before expiry'),('Scoped retirement exceeded fixed session','Retirement session expired'),('Selected flow had no bidirectional traffic before bounded getter deadline','No timely bidirectional tag traffic'),('Complete retirement evidence must contain both exact instances','Both exact instances required')]:
    s=s.replace(before,after)
p.write_text(s,encoding='utf-8',newline='\n')
r=Path('work/nss129');(r/'sizing-correction-private.json').write_text(json.dumps({'firstQualificationFailurePreserved':True,'harnessWrongShapeIncludedDuplicateNftBatch':True,'actualProductionShapeInitialBytes':75715,'afterLexicalPackingBytes':75096,'unchangedLimit':73728,'newRetirementAssertionsUnchanged':True,'deletedOptionalObserverMetadataOnly':True,'productionWrites':False})+'\n')
print('TRIMMED_OPTIONAL_METADATA_ONLY')
