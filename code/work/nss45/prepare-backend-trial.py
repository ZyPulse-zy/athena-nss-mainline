"""Bind a backend-only temporary trial to the proven checkpoint/expiry pipeline."""
import hashlib,json,subprocess
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
dep=json.loads((root/'work/nss39/deployment-latest.json').read_text(encoding='utf-8-sig'))
cfg=json.loads((root/dep['localDir']/'config.json').read_text(encoding='utf-8-sig'))
qualified=json.loads((here/'recovery-qualified.json').read_text());bench=json.loads((here/'recovery-readonly-qualified.json').read_text())
assert qualified['passed'] and bench['passed'] and all(r['passed']and r['checks']==24 for r in qualified['results'])
backend=(here/'candidate-backend.lua').read_bytes();assert sha(backend)==bench['candidateSha256']==qualified['results'][1]['sourceSha256']
stage=here/'backend-trial';stage.mkdir(exist_ok=True)
for name in ['worker.lua','guardian.lua','conntrack-source.lua']:
    b=(root/'athena-nss-mainline/code/deployed-classifier'/name).read_bytes();assert sha(b)==cfg['files'][name];(stage/name).write_bytes(b)
(stage/'backend.lua').write_bytes(backend)
s=(root/'work/nss39/upgrade.mjs').read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
start=s.index("const root='work/nss39'");end=s.index("const id='nss39-'")
s=s[:start]+r'''const root='work/nss45/backend-trial',old=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json')),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),json=o=>JSON.stringify(o,null,2)+'\n';assert.equal(old.committed,true);
const qualified=JSON.parse(fs.readFileSync('work/nss45/recovery-qualified.json')),bench=JSON.parse(fs.readFileSync('work/nss45/recovery-readonly-qualified.json'));assert.ok(qualified.passed&&bench.passed);assert.equal(qualified.results[1].sourceSha256,sha(fs.readFileSync(root+'/backend.lua')));assert.equal(bench.candidateSha256,qualified.results[1].sourceSha256);assert.ok(qualified.results.every(r=>r.passed&&r.checks===24));
const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));for(const n of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(sha(fs.readFileSync(root+'/'+n)),previousConfig.files[n]);
''' +s[end:]
replace("const id='nss39-'","const id='nss45-backend-'")
replace("const extraNames=['guardian.lua','conntrack-source.lua']","const extraNames=['guardian.lua','conntrack-source.lua','backend.lua']")
replace("normalized.files['worker.lua']=previousConfig.files['worker.lua']","normalized.files['backend.lua']=previousConfig.files['backend.lua']")
replace("Only tc child supervision and mutation diagnostics may change","Only initial recovery enumeration reuse and configuration binding may change")
replace("NEW_SOURCE:sha(extras['conntrack-source.lua'].new)","NEW_SOURCE:sha(extras['conntrack-source.lua'].new),OLD_BACKEND:sha(extras['backend.lua'].old),NEW_BACKEND:sha(extras['backend.lua'].new)")
replace("test \"$(sha256sum __BACKUP__/old-conntrack-source.lua|cut -d' ' -f1)\" = __OLD_SOURCE__\n", "test \"$(sha256sum __BACKUP__/old-conntrack-source.lua|cut -d' ' -f1)\" = __OLD_SOURCE__\ntest \"$(sha256sum __BACKUP__/old-backend.lua|cut -d' ' -f1)\" = __OLD_BACKEND__\ncp __BACKUP__/old-backend.lua __BASE__/backend.lua.new\nchmod 600 __BASE__/backend.lua.new\nmv __BASE__/backend.lua.new __BASE__/backend.lua\n")
replace("['new-worker.lua','new-guardian.lua','new-conntrack-source.lua']","['new-worker.lua','new-guardian.lua','new-conntrack-source.lua','new-backend.lua']")
replace("\\nprintf ready >__BACKUP__/ready\\n", "\\ncp '+stage.ready.dir+'/old-backend.lua __BACKUP__/old-backend.lua\\ntest \"$(sha256sum __BACKUP__/old-backend.lua|cut -d\\' \\' -f1)\" = __OLD_BACKEND__\\nprintf ready >__BACKUP__/ready\\n")
replace("test \"$(sha256sum __BASE__/conntrack-source.lua|cut -d' ' -f1)\" = __OLD_SOURCE__\n", "test \"$(sha256sum __BASE__/conntrack-source.lua|cut -d' ' -f1)\" = __OLD_SOURCE__\ntest \"$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)\" = __OLD_BACKEND__\ncp __STAGE__/new-backend.lua __BASE__/backend.lua.new\nchmod 600 __BASE__/backend.lua.new\nmv __BASE__/backend.lua.new __BASE__/backend.lua\n")
replace("test \"$(sha256sum __BASE__/config.json|cut -d' ' -f1)\" = __NEW_HASH__\n", "test \"$(sha256sum __BASE__/config.json|cut -d' ' -f1)\" = __NEW_HASH__\ntest \"$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)\" = __NEW_BACKEND__\n")
replace('tcChildSupervisionTrial:true','initialRecoveryReadReuseTrial:true')
(here/'upgrade-backend.mjs').write_text(s,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
r=subprocess.run([node,'--check',str(here/'upgrade-backend.mjs')],capture_output=True,text=True,timeout=20);assert r.returncode==0,r.stderr
assert s.index('checkpoint.sh before-')<s.index('stage-guardian.lua')<s.index('transaction.sh arm')<s.index('const rollbackProof=')<s.index('const install=')
out={'passed':True,'scriptSha256':sha(s.encode()),'templateSha256':sha((root/'work/nss39/upgrade.mjs').read_bytes()),'backendSha256':sha(backend),'productionSourcesChanged':['backend.lua'],'workerGuardianAndSourceUnchanged':True,'classifierPolicyAndNssPermissionUnchanged':True,'checkpointBeforeStaging':True,'independentStageExpirySeconds':480,'independentTransactionExpirySeconds':180,'rollbackRestoresBackendAndConfig':True,'nssEnabled':False,'scope':'Backend-only temporary trial; uses prior checkpoint/independent expiry pipeline. Must observe actual expiry restoration before claiming qualified.'}
(here/'backend-trial-prepared.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items()if 'Sha256'not in k}))
