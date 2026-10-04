"""Freeze only an explicit list of readable source; never traverse raw evidence."""
import hashlib,json,shutil
from pathlib import Path

root=Path(__file__).resolve().parents[2]
entryNames=['audit-renderer.mjs','binding.mjs','build-entry.mjs','classified-tags.lua','classifier.lua','core-guard-phase.lua','current-audit-diagnostic.mjs','dependency-closure.mjs','entry-scheduling-fixtures.lua','fast-path.lua','final-closure.mjs','inspect-classifier.mjs','module-stage-guardian.lua','module-stage.mjs','parse-dependency-graph.mjs','parse-ecm-any-wan.mjs','payload.mjs','prepare-entry.py','publication-wait-fixtures.lua','publication-wait.lua','qos-physical.lua','qualification.mjs','read-prerequisites.lua','read-real-candidates.mjs','real-session.mjs','record-candidates.mjs','session-binding.mjs','state-node.lua','tag-normalizer.lua','test-binding.mjs','test-controller.mjs','test-dependencies.mjs','test-entry-scheduling.py','test-parser.mjs','test-publication-wait.py','wait-ready-candidate.mjs','wan-scope.lua']
allow={
 'nss47':['audit-cache-retain.mjs','audit-cache.mjs','build-cache.py','build-core.py','cache-bound-replay.lua','classifier-core-cache.lua','classifier-core.lua','commit-cache.mjs','native-cache.mjs','native-core.mjs','prepare-cache-retain.py','prepare-cache-trial.py','profile-publication.mjs','test-cache-bound.py','test-cache.py','test-core.py','upgrade-cache-retain.mjs','upgrade-cache.mjs','verify-cache-rollback.mjs'],
 'nss48':entryNames,
 'nss49':entryNames+['aba-fixtures.lua','analyze-aba.mjs','clock-anchor.mjs','native-qualification.mjs','preflight-mainline.mjs','prepare-final-closure.py','final-cleanup-audit.mjs','summarize.py','render-report.py','freeze-safe-sources.py']
}
for round,names in allow.items():
    hashes={}
    base=root/'work'/round
    proof=base/'source-proof-v1.json'
    assert not proof.exists(),'Do not rewrite frozen source proof'
    frozen=base/'proof-v1'/'code';frozen.mkdir(parents=True)
    for name in names:
        file=base/name;body=file.read_bytes();body.decode('utf-8')
        assert 'private' not in name and file.suffix in ['.lua','.mjs','.py']
        destination=frozen/name
        assert not destination.exists()
        shutil.copyfile(file,destination)
        hashes['work/'+round+'/'+name]=hashlib.sha256(body).hexdigest()
        assert hashlib.sha256(destination.read_bytes()).hexdigest()==hashes['work/'+round+'/'+name]
    out={'version':1,'sources':len(hashes),'sourceHashes':hashes,'privateConnectionAndCapturesExcluded':True,'notAdditionalProductionAdmission':True}
    with proof.open('x',encoding='utf-8',newline='\n') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'round':round,'frozenReadableSources':len(hashes),'privateCapturesCopied':False}))
