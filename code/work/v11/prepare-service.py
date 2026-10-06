"""Package the proven lifecycle without changing router-side Lua or the gate."""
from pathlib import Path

root = Path(__file__).resolve().parent
prior = root.with_name('nss160')

def create(name, text):
    with (root / name).open('x', encoding='utf-8', newline='') as f:
        f.write(text)

reader = (prior / 'read-real-candidates-v3.mjs').read_text(encoding='utf-8')
reader = reader.replace("from'./application-ownership.mjs'", "from'../nss160/application-ownership.mjs'")
reader = reader.replace('work/nss160/', 'work/v11/')
create('read-real-candidates.mjs', reader)

recorder = (prior / 'record-candidates-v3.mjs').read_text(encoding='utf-8')
recorder = recorder.replace('./session-binding-v3.mjs', './session-binding.mjs')
recorder = recorder.replace('work/nss160/', 'work/v11/')
recorder = recorder.replace('read-real-candidates-v3.mjs', 'read-real-candidates.mjs')
create('record-candidates.mjs', recorder)

audit = (prior / 'current-audit-diagnostic.mjs').read_text(encoding='utf-8')
audit = audit.replace("from './declared-baseline.mjs'", "from '../nss160/declared-baseline.mjs'")
audit = audit.replace(r'/^work\/nss160\/(?:automatic-epoch|controlled-class|real-matched-aba)-\d+-[a-f0-9]+$/', r'/^work\/v11\/session-\d+-[a-f0-9]+$/')
assert r'assert.match(caseDir,/^work\/v11\/session-' in audit
audit = audit.replace("readBaseline(c,'work/nss160',", "readBaseline(c,'work/v11',")
audit = audit.replace("writeFileSync('work/nss160/'+label", "writeFileSync('work/v11/'+label")
create('current-audit-diagnostic.mjs', audit)

stage = (root.with_name('nss158') / 'module-stage.mjs').read_text(encoding='utf-8')
assert stage.count('work/nss158/fast-path.lua') == 1
stage = stage.replace('work/nss158/fast-path.lua', 'work/nss157/fast-path-v2.lua')
create('module-stage.mjs', stage)
create('payload.mjs', "// Exact proven single-B lifecycle; no new native source or bytecode.\nexport {buildPayload} from '../nss157/payload-v4.mjs';\n")

entry = (prior / 'real-session-v4.mjs').read_text(encoding='utf-8')
entry = entry.replace("from'./declared-baseline.mjs'", "from'../nss160/declared-baseline.mjs'")
entry = entry.replace('./session-binding-v4.mjs', './session-binding.mjs')
entry = entry.replace('../nss158/module-stage.mjs', './module-stage.mjs')
entry = entry.replace("['inspect','aba']", "['inspect','session']")
entry = entry.replace("observationRoot='work/nss160'", "observationRoot='work/v11'")
entry = entry.replace('record-candidates-v3.mjs', 'record-candidates.mjs')
entry = entry.replace('work/nss160/real-matched-aba-', 'work/v11/session-')
entry = entry.replace('work/nss160/current-audit-diagnostic.mjs', 'work/v11/current-audit-diagnostic.mjs')
entry = entry.replace("['abaCompleted','unchangedQoSPlan'", "['automaticLifecycleEpochCompleted','unchangedQoSPlan'")
entry = entry.replace("['A','B','A2']", "['B']")
entry = entry.replace("p.name==='B'?2:0", '2')
entry = entry.replace('matchedForwardingABA:true', 'boundedSingleNssSession:true,matchedForwardingABA:false')
entry = entry.replace("mode:'aba'", "mode:'session'")
entry = entry.replace('matchedForwardingABARequested:true,matchedForwardingABACompleted:completed', 'matchedForwardingABARequested:false,boundedSessionCompleted:completed')
entry = entry.replace('// Identical queue budget and common observer across A/B/A2. Real offered load and\n// game telemetry still need review before any performance conclusion.', '// One proven 20-second NSS lifecycle, with no A/A2 or performance benchmark.\n// The hard native session, fresh classification, exact pins and recovery are unchanged.')
needle="verifyPreparation();\nconst proof="
assert entry.count(needle) == 1
entry=entry.replace(needle, "verifyPreparation();\nconst control=process.argv[3];const pinnedWan=process.argv[4]?Number(process.argv[4]):null;\nif(control)assert.match(control,/^work\\/v11\\/runtime\\/run-[a-f0-9]{32}\\/stop-request\\.json$/);\nfunction checkStop(){assert.ok(!control||!fs.existsSync(control),'STOP_REQUESTED_NO_FURTHER_ADMISSION');}\ncheckStop();\nconst proof=")
entry=entry.replace('const pair=selectRealPair(candidates);', 'const pair=selectRealPair(candidates).filter(p=>pinnedWan===null||p.g.identity.wan===pinnedWan);')
entry=entry.replace("const preauditSelected={tcp:convert(pair[0].b),udp:convert(pair[0].g)};let selected;", "const preauditSelected={tcp:convert(pair[0].b),udp:convert(pair[0].g)};let selected;\n assert.ok(pinnedWan===null||preauditSelected.udp.wan===pinnedWan);checkStop();")
entry=entry.replace('context=await beginStage(', 'checkStop();\n  context=await beginStage(')
entry=entry.replace('verifyPreparation();runNode(observationRoot', 'checkStop();verifyPreparation();runNode(observationRoot')
entry=entry.replace('await uploadStage(context);let latest;', 'checkStop();await uploadStage(context);let latest;')
entry=entry.replace('let c,context,before,completed=false;', 'let c,context,before,completed=false,recoveryVerified=false;')
needle="save('baseline-audit',auditScopedBaseline(before,after));"
assert entry.count(needle)==1
entry=entry.replace(needle, needle+'recoveryVerified=true;')
entry=entry.replace('gameQualityConclusion:false,errors:failures', 'gameQualityConclusion:false,recoveryVerified,independentOwnerStarted:!!context,errors:failures')
entry=entry.replace("output:dir,errors:failures", "output:dir,recoveryVerified,independentOwnerStarted:!!context,errors:failures")
create('session.mjs', entry)
print('Created isolated host integration; native lifecycle, guardian and all old inputs retained')
