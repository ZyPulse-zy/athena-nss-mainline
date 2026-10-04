"""Bind the unchanged NSS data plane to the retained pure parser cache."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
names=['fast-path.lua','classifier.lua','core-guard-phase.lua','classified-tags.lua','qos-physical.lua','tag-normalizer.lua','wan-scope.lua','state-node.lua','module-stage-guardian.lua','read-prerequisites.lua','publication-wait.lua']
for name in names:
    assert not(here/name).exists();(here/name).write_bytes((root/'work/nss46'/name).read_bytes())
for name in ['aba-qualified.json','consumer-qualified.json','mainline-preflight-qualified.json']:
    (here/name).write_bytes((root/'work/nss46'/name).read_bytes())
scripts=['qualification.mjs','session-binding.mjs','dependency-closure.mjs','parse-dependency-graph.mjs','current-audit-diagnostic.mjs','audit-renderer.mjs','real-session.mjs','module-stage.mjs','payload.mjs','record-candidates.mjs','read-real-candidates.mjs','parse-ecm-any-wan.mjs','wait-ready-candidate.mjs','inspect-classifier.mjs','final-closure.mjs','build-entry.mjs','test-parser.mjs','test-controller.mjs','test-dependencies.mjs','test-binding.mjs','test-entry-scheduling.py']
for name in scripts:
    if name=='audit-renderer.mjs':
        (here/name).write_bytes((root/'work/nss46'/name).read_bytes())
        continue
    s=(root/'work/nss46'/name).read_text().replace('work/nss46','work/nss48')
    if name=='build-entry.mjs':
        s=s.replace("for(const name of ['config.json','worker.lua','guardian.lua','conntrack-source.lua','backend.lua'])", "for(const name of ['config.json','worker.lua','guardian.lua','conntrack-source.lua','backend.lua','classifier-core.lua'])")
        s=s.replace("const tests={};", "for(const file of ['work/nss47/classifier-core-cache.lua','work/nss47/cache-qualified.json','work/nss47/native-cache-qualified.json','work/nss47/cache-bound-qualified.json','work/nss47/deployment-latest.json'])sourceManifest[file]=hash(file);const tests={};")
        s=s.replace("round:'NSS46'","round:'NSS48'")
    (here/name).write_text(s,encoding='utf-8',newline='\n')
(here/'deployment-latest.json').write_bytes((root/'work/nss47/deployment-latest.json').read_bytes())
binding="""import assert from'node:assert/strict';
import {verifyCurrentClassifier as historical,read,hash}from'../nss46/binding.mjs';
export {read,hash};
export function verifyCurrentClassifier(){
 const original=historical(),deployment=read('work/nss48/deployment-latest.json');assert.ok(deployment.committed&&deployment.permanentClassifier&&deployment.nssEnabled===false);
 const config=read(deployment.localDir+'/config.json');assert.equal(hash(deployment.localDir+'/config.json'),deployment.configHash);
 const delta=read('work/nss47/cache-delta.json'),pure=read('work/nss47/cache-qualified.json'),native=read('work/nss47/native-cache-qualified.json'),bound=read('work/nss47/cache-bound-qualified.json');
 assert.ok(pure.passed&&native.passed&&bound.passed&&native.parserMetadataEqual&&native.completeClassifierRepeatedEqual===3);
 for(const proof of [pure,native,bound]){assert.equal(proof.originalSha256,original.config.files['classifier-core.lua']);assert.equal(proof.candidateSha256,config.files['classifier-core.lua']);}
 assert.equal(config.files['classifier-core.lua'],hash('work/nss47/classifier-core-cache.lua'));assert.equal(config.files['classifier-core.lua'],hash(deployment.localDir+'/classifier-core.lua'));
 const trial=read('work/nss47/cache-trial/deployment-latest.json'),undo=read(trial.localDir+'/rollback-qualified.json');assert.ok(undo.passed&&undo.automaticExpiryWithoutControllerRollback&&undo.previousClassifierCoreRestored);
 const commit=read(deployment.localDir+'/permanent-commit.json'),audit=read(deployment.localDir+'/permanent-before-commit-audit.json');assert.ok(commit.committed&&audit.passed&&audit.originalCompleteAuditAssertionsRetained);assert.equal(commit.configHash,deployment.configHash);
 for(const name of ['worker.lua','guardian.lua','conntrack-source.lua','backend.lua']){assert.equal(config.files[name],original.config.files[name]);assert.equal(hash(deployment.localDir+'/'+name),config.files[name]);}
 const normalized=structuredClone(config);normalized.files['classifier-core.lua']=original.config.files['classifier-core.lua'];normalized.installTransaction=original.config.installTransaction;assert.deepEqual(normalized,original.config,'Only independently qualified pure address cache and owner binding may change');
 const configuration={...original.configuration,configSha256:deployment.configHash,classifierCoreSha256:config.files['classifier-core.lua'],pureParserCacheQualified:true};return{deployment,config,configuration};
}
"""
(here/'binding.mjs').write_text(binding,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in scripts+['binding.mjs']:
    if name.endswith('.mjs'):subprocess.run([node,'--check',str(here/name)],check=True)
print(json.dumps({'prepared':True,'entry':'NSS48','classifierReference':'work/nss47/deployment-latest.json','nssLuaUnchanged':True,'ownerAndAdmissionDeadlinesUnchanged':True,'controlledBudgetMbps':20,'flowCount':2}))
