"""Freeze explicit readable source lists; never copy a private receipt or screenshot."""
import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2]
allow={
'nss50':['service-epoch.mjs','current-audit-diagnostic.mjs','session-binding.mjs','real-session.mjs','test-service-epoch.mjs','qualify-overlay.mjs','clock-anchor.mjs','cleanup-audit.mjs','inspect-selected.mjs','capture-hud.js','capture-hud-long.js','analyze-aba.mjs','map-client-frames.mjs','make-hud-sheet.py','analyze-partial.mjs'],
'nss51':['build-candidate.mjs','core-guard-phase.lua','phase-delta.json','qualify-phase.mjs','build-entry.mjs','module-stage.mjs','real-session.mjs','current-audit-diagnostic.mjs','qualification.mjs','session-binding.mjs','qualify-entry.mjs','trace-phase.mjs','trace-exact-observer.mjs','summarize-traces.mjs'],
'nss52':['build-candidate.mjs','core-guard-phase.lua','phase-delta.json','qualify-phase.mjs','summarize.py','render-report.py','freeze-safe-sources.py']}
for round,names in allow.items():
    base=root/'work'/round;proof=base/'source-proof-v1.json';assert not proof.exists()
    frozen=base/'proof-v1'/'code';frozen.mkdir(parents=True)
    hashes={}
    for name in names:
        assert 'private'not in name
        body=(base/name).read_bytes();body.decode('utf-8');dst=frozen/name;assert not dst.exists();shutil.copyfile(base/name,dst)
        digest=hashlib.sha256(body).hexdigest();assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
        hashes['work/'+round+'/'+name]=digest
    result={'version':1,'sources':len(hashes),'sourceHashes':hashes,'privateConnectionAndCapturesExcluded':True,'notAdditionalProductionAdmission':True,'phase52ProductionEntryQualified':False}
    with proof.open('x',encoding='utf-8',newline='\n')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'round':round,'frozenReadableSources':len(hashes),'rawEvidenceCopied':False}))
