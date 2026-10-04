"""Change only bounded row-overload handling in a separate expiry trial."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
dep=json.loads((root/'work/nss39/deployment-latest.json').read_text());cfg=json.loads((root/dep['localDir']/'config.json').read_text())
q=json.loads((here/'row-qualified.json').read_text());n=json.loads((here/'row-native-replay-qualified.json').read_text());syntax=json.loads((here/'row-native-syntax-qualified.json').read_text());query=json.loads((here/'query-cleanup-native-qualified.json').read_text())
assert q['passed']and q['checks']==48 and n['passed']and n['checks']==48 and syntax['passed']and query['passed']and query['checks']==7
trial=here/'row-trial';trial.mkdir(exist_ok=True)
for name in ['worker.lua','guardian.lua','conntrack-source.lua']:
    b=(here/name).read_bytes();assert sha(b)==q['sources'][name]==syntax['sourceHashes'][name];(trial/name).write_bytes(b)
b=(here/'original-backend.lua').read_bytes();assert sha(b)==cfg['files']['backend.lua'];(trial/'backend.lua').write_bytes(b)
s=(here/'upgrade-backend.mjs').read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,a;s=s.replace(a,b)
replace("root='work/nss45/backend-trial'","root='work/nss45/row-trial'")
a=s.index('const qualified=');b=s.index("const id='nss45-backend-'")
s=s[:a]+r'''const qualified=JSON.parse(fs.readFileSync('work/nss45/row-qualified.json')),native=JSON.parse(fs.readFileSync('work/nss45/row-native-replay-qualified.json')),syntax=JSON.parse(fs.readFileSync('work/nss45/row-native-syntax-qualified.json')),query=JSON.parse(fs.readFileSync('work/nss45/query-cleanup-native-qualified.json'));
assert.ok(qualified.passed&&native.passed&&syntax.passed&&query.passed);assert.equal(qualified.checks,48);assert.equal(native.checks,48);assert.equal(query.checks,7);
const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));for(const name of ['worker.lua','guardian.lua','conntrack-source.lua']){const hash=sha(fs.readFileSync(root+'/'+name));assert.equal(hash,qualified.sources[name]);assert.equal(hash,syntax.sourceHashes[name])}assert.equal(sha(fs.readFileSync(root+'/backend.lua')),previousConfig.files['backend.lua']);
'''+s[b:]
replace("const id='nss45-backend-'","const id='nss45-row-'")
replace("normalized.files['backend.lua']=previousConfig.files['backend.lua'];", "for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])normalized.files[name]=previousConfig.files[name];")
replace('Only initial recovery enumeration reuse and configuration binding may change','Only bounded source-row failure handling and configuration binding may change')
replace('initialRecoveryReadReuseTrial:true','boundedSourceRowOverloadTrial:true')
(here/'upgrade-row.mjs').write_text(s,encoding='utf-8',newline='\n')
names=['audit-row-trial.mjs','observe-row-trial.mjs','verify-row-rollback.mjs']
for target,original in zip(names,['audit-backend-trial.mjs','observe-backend-trial.mjs','verify-backend-rollback.mjs']):
    body=(here/original).read_text().replace('work/nss45/backend-trial','work/nss45/row-trial').replace('backendOnlyTrial:true','boundedRowOverloadOnlyTrial:true')
    (here/target).write_text(body,encoding='utf-8',newline='\n')
body=(here/'final-closure.mjs').read_text().replace('work/nss45/final-closure.json','work/nss45/backend-closure.json');(here/'closure-backend.mjs').write_text(body,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-row.mjs','closure-backend.mjs']+names:
    p=subprocess.run([node,'--check',str(here/name)],capture_output=True,text=True,timeout=20);assert p.returncode==0,p.stderr
assert s.index('checkpoint.sh before-')<s.index('stage-guardian.lua')<s.index('transaction.sh arm')<s.index('const rollbackProof=')<s.index('const install=')
proof={'passed':True,'changedProductionSemantics':['bounded-source-row-overflow'],'backendAndClassifierPolicyUnchanged':True,'sourceRowLimit':2048,'sourceBytesLimit':524288,'queryAgeSeconds':2,'mutationDeadlineSeconds':6,'nssEnabled':False,'independentTransactionExpirySeconds':180,'independentStageExpirySeconds':480,'checkpointBeforeStaging':True,'previousFourClassifierSourcesAndConfigRestoredByUndo':True,'scriptSha256':sha(s.encode()),'sources':q['sources'],'observerSources':{n:sha((here/n).read_bytes())for n in names},'noInstallationYet':True}
(here/'row-trial-prepared.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items()if k not in ['sources','observerSources']}))
