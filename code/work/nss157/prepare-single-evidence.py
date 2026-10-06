from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'fast-path.lua').read_text(encoding='utf-8')
assert s.count('   R.rejectedComparison=C\n')==1
s=s.replace('   R.rejectedComparison=C\n','')
s=s.replace("if supported then retire(C);return{terminalReason='AUTHENTICATED_BULK_TO_BE',comparison=C}end", "if supported then retire(C);return{terminalReason='AUTHENTICATED_BULK_TO_BE',comparisonRecord='actualReclassification'}end")
s=s.replace("    return{terminalReason='AUTHENTICATED_PAIR_NO_LONGER_ADMITTED',comparison=C}","    R.rejectedComparison=C;return{terminalReason='AUTHENTICATED_PAIR_NO_LONGER_ADMITTED',comparisonRecord='rejectedComparison'}")
assert s.count('comparison=O.comparison,')==1
s=s.replace('comparison=O.comparison,','comparisonRecord=O.comparisonRecord,')
put('fast-path-v2.lua',s)
put('payload-v4.mjs',(r/'payload-v3.mjs').read_text(encoding='utf-8').replace("'work/nss157/fast-path.lua'","'work/nss157/fast-path-v2.lua'"))
s=(r/'combined-models.lua').read_text(encoding='utf-8')
s=s.replace("return{case=kind,passed=true,actualObserveRetireTickRunFunctions=true,mockedBackend=true,hardwareProof=false}","local wire=assert(j.parse(j.stringify(R)));if kind=='supported-class'then assert(wire.actualReclassification.action=='RETIRE_EXACT_SELECTED_SLOTS'and wire.actualReclassification.evidence.completeSelected.slots.tcp.class=='BE');assert(wire.rejectedComparison==nil and wire.terminalInvalidation.comparisonRecord=='actualReclassification')elseif kind=='unsupported-class'or kind=='projection-missing'or kind=='identity-drift'then assert(wire.rejectedComparison.action=='RETIRE_EXACT_SELECTED_SLOTS'and wire.terminalInvalidation.comparisonRecord=='rejectedComparison')end;return{case=kind,passed=true,actualObserveRetireTickRunFunctions=true,wireEvidencePreserved=true,mockedBackend=true,hardwareProof=false}")
s=s.replace("local cases={};local M={tagEpoch=function()end}","local alias={action='MODEL_ONLY'};local wire=assert(j.parse(j.stringify({first=alias,second=alias})));assert((wire.first and 1 or 0)+(wire.second and 1 or 0)==1,'Native encoder alias behavior changed');local cases={};local M={tagEpoch=function()end}")
s=s.replace('backendMocked=true}))','backendMocked=true,nativeSharedAliasNullReproduced=true}))')
put('combined-models-v2.lua',s)
s=(r/'qualify-native.mjs').read_text(encoding='utf-8').replace("'./payload-v2.mjs'","'./payload-v4.mjs'").replace("dir=root+'/native-qualification-v1'","dir=root+'/native-qualification-v2'").replace("root+'/fast-path.lua'","root+'/fast-path-v2.lua'").replace("root+'/combined-models.lua'","root+'/combined-models-v2.lua'").replace("classifier:'work/nss149/classifier.lua'","classifier:'work/nss157/classifier-complete-wait.lua'").replace("root+'/native-qualified.json'","root+'/native-qualified-v2.json'").replace('model.checks===9&&!model.fullFactoryModeled','model.checks===9&&model.nativeSharedAliasNullReproduced&&!model.fullFactoryModeled').replace('filesWrittenOnRouter:false','filesWrittenOnRouter:false,evidenceRecordedExactlyOnceAndTerminalUsesFieldReference:true,originalPreciseGateRetirementBodyUnchanged:true')
put('qualify-native-v2.mjs',s)
print('Each full comparison recorded once; terminal field reference avoids native JSON alias null, gate/retirement body unchanged.')
