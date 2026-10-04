"""Derive a classifier-core-only trial with the proven independent undo pipeline."""
from pathlib import Path
import json,hashlib,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
dep=json.loads((root/'work/nss46/deployment-latest.json').read_text());cfg=json.loads((root/dep['localDir']/'config.json').read_text())
q=json.loads((here/'native-cache-qualified.json').read_text());assert q['passed'] and q['parserMetadataEqual'] and q['completeClassifierRepeatedEqual']==3
trial=here/'cache-trial';trial.mkdir(exist_ok=True)
for name in ['worker.lua','guardian.lua','conntrack-source.lua','backend.lua']:
    data=(root/dep['localDir']/name).read_bytes();assert sha(data)==cfg['files'][name];(trial/name).write_bytes(data)
data=(here/'classifier-core-cache.lua').read_bytes();assert sha(data)==q['candidateSha256'];(trial/'classifier-core.lua').write_bytes(data)
s=(root/'work/nss46/upgrade-row.mjs').read_text()
s=s.replace("root='work/nss46/row-retain'","root='work/nss47/cache-trial'")
a=s.index('const qualified=');b=s.index("const id='nss46-row-'")
s=s[:a]+"""const qualified=JSON.parse(fs.readFileSync('work/nss47/cache-qualified.json')),native=JSON.parse(fs.readFileSync('work/nss47/native-cache-qualified.json'));assert.ok(qualified.passed&&native.passed&&native.parserMetadataEqual&&native.completeClassifierRepeatedEqual===3);assert.equal(qualified.candidateSha256,native.candidateSha256);assert.equal(native.candidateSha256,sha(fs.readFileSync(root+'/classifier-core.lua')));const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));assert.equal(previousConfig.files['classifier-core.lua'],native.originalSha256);for(const name of ['worker.lua','guardian.lua','conntrack-source.lua','backend.lua'])assert.equal(sha(fs.readFileSync(root+'/'+name)),previousConfig.files[name]);
"""+s[b:]
s=s.replace("const id='nss46-row-'","const id='nss47-cache-'")
s=s.replace("const extraNames=['guardian.lua','conntrack-source.lua','backend.lua']","const extraNames=['guardian.lua','conntrack-source.lua','backend.lua','classifier-core.lua']")
s=s.replace("'work/nss23/'+n","(n==='classifier-core.lua'?'work/nss29/'+n:'work/nss23/'+n)")
s=s.replace("for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])normalized.files[name]=previousConfig.files[name];","normalized.files['classifier-core.lua']=previousConfig.files['classifier-core.lua'];")
s=s.replace('Only qualified bounded row-overflow handling and binding may change','Only qualified per-observation pure address cache and owner binding may change')
s=s.replace("NEW_BACKEND:sha(extras['backend.lua'].new)","NEW_BACKEND:sha(extras['backend.lua'].new),OLD_CORE:sha(extras['classifier-core.lua'].old),NEW_CORE:sha(extras['classifier-core.lua'].new)")
def replace(a,b,count=1):
    global s
    assert s.count(a)==count,(a,s.count(a));s=s.replace(a,b)
replace("test \"$(sha256sum __BACKUP__/old-backend.lua|cut -d' ' -f1)\" = __OLD_BACKEND__", "test \"$(sha256sum __BACKUP__/old-classifier-core.lua|cut -d' ' -f1)\" = __OLD_CORE__\ncp __BACKUP__/old-classifier-core.lua __BASE__/classifier-core.lua.new\nchmod 600 __BASE__/classifier-core.lua.new\nmv __BASE__/classifier-core.lua.new __BASE__/classifier-core.lua\ntest \"$(sha256sum __BACKUP__/old-backend.lua|cut -d' ' -f1)\" = __OLD_BACKEND__")
replace("'new-conntrack-source.lua','new-backend.lua'","'new-conntrack-source.lua','new-backend.lua','new-classifier-core.lua'")
replace("\\nprintf ready >__BACKUP__/ready\\n", "\\ncp '+stage.ready.dir+'/old-classifier-core.lua __BACKUP__/old-classifier-core.lua\\ntest \"$(sha256sum __BACKUP__/old-classifier-core.lua|cut -d\\' \\' -f1)\" = __OLD_CORE__\\nprintf ready >__BACKUP__/ready\\n")
replace("test \"$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)\" = __OLD_BACKEND__", "test \"$(sha256sum __BASE__/classifier-core.lua|cut -d' ' -f1)\" = __OLD_CORE__\ncp __STAGE__/new-classifier-core.lua __BASE__/classifier-core.lua.new\nchmod 600 __BASE__/classifier-core.lua.new\nmv __BASE__/classifier-core.lua.new __BASE__/classifier-core.lua\ntest \"$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)\" = __OLD_BACKEND__")
replace("test \"$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)\" = __NEW_BACKEND__", "test \"$(sha256sum __BASE__/backend.lua|cut -d' ' -f1)\" = __NEW_BACKEND__\ntest \"$(sha256sum __BASE__/classifier-core.lua|cut -d' ' -f1)\" = __NEW_CORE__")
s=s.replace('qualifiedRowOverloadRetention:true','qualifiedPureAddressCacheTrial:true')
(here/'upgrade-cache.mjs').write_text(s,encoding='utf-8',newline='\n')
a=(root/'work/nss46/audit-row.mjs').read_text().replace("from './audit-renderer.mjs'","from '../nss46/audit-renderer.mjs'").replace('work/nss46/row-retain/deployment-latest.json','work/nss47/cache-trial/deployment-latest.json').replace('qualifiedRowOverloadRetention:true','qualifiedPureAddressCacheTrial:true')
(here/'audit-cache.mjs').write_text(a,encoding='utf-8',newline='\n')
v=(root/'work/nss46/verify-fault-rollback.mjs').read_text().replace('work/nss46/expiry-fault/deployment-latest.json','work/nss47/cache-trial/deployment-latest.json').replace("'/backend.lua');","'/backend.lua '+previous.base+'/classifier-core.lua');").replace("['conntrack-source.lua','guardian.lua','backend.lua']","['conntrack-source.lua','guardian.lua','backend.lua','classifier-core.lua']").replace('realApplyExpiryFaultTrial:true','pureAddressCacheTrial:true,previousClassifierCoreRestored:true')
(here/'verify-cache-rollback.mjs').write_text(v,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-cache.mjs','audit-cache.mjs','verify-cache-rollback.mjs']:
    subprocess.run([node,'--check',str(here/name)],check=True)
print(json.dumps({'prepared':True,'singleVariable':'classifier-core pure address caching','otherFourPayloadFilesIdentical':True,'independentRollbackSeconds':180,'stagingLifetimeSeconds':480,'nssEnabled':False}))
