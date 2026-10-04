"""One real-watch timing fault under the existing independent rollback."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def emit(name,s):(here/name).write_text(s,encoding='utf-8',newline='\n')
w=(here/'fault-worker.lua').read_text()
needle=" assert(rc==0,'Classifier mutation child failed; action='..action..'; rawStatus='..tostring(rc)..'; elapsed='..tostring(now()-mutationBegan))"
assert w.count(needle)==1
w=w.replace(needle," io.stdout:write('NSS46_REAL_MUTATION action='..action..' rawStatus='..tostring(rc)..' elapsed='..tostring(now()-mutationBegan)..'\\n');io.stdout:flush()\n"+needle)
needle=' atomic(ram..\'/apply-result.json\',v);os.exit(0)'
assert w.count(needle)==1
w=w.replace(needle," local child=assert(proc(n.getpid()));v.testRuntime={testOnly=true,pid=child.pid,start=child.start,parent=child.parent,producerPid=req.pid,producerStart=req.start,fd8TransactionLocked=true,fd9LifetimeLocked=true,checkedAt=now()}\n"+needle)
emit('fault-worker.lua',w)
trial=here/'expiry-fault';trial.mkdir()
for name,origin in [('worker.lua',here/'fault-worker.lua'),('guardian.lua',here/'stale-guardian.lua'),('conntrack-source.lua',root/'work/nss45/original-conntrack-source.lua'),('backend.lua',root/'work/nss45/candidate-backend.lua')]:
    (trial/name).write_bytes(origin.read_bytes())
s=(root/'work/nss45/upgrade-backend.mjs').read_text().replace("root='work/nss45/backend-trial'","root='work/nss46/expiry-fault'").replace("fs.readFileSync('work/nss39/deployment-latest.json')","fs.readFileSync('work/nss46/deployment-latest.json')")
a=s.index('const qualified=');b=s.index("const id='nss45-backend-'")
s=s[:a]+"""const qualified=JSON.parse(fs.readFileSync('work/nss46/stale-qualified.json')),fault=JSON.parse(fs.readFileSync('work/nss46/fault-prepared.json'));assert.ok(qualified.passed&&qualified.checks===34&&fault.passed);assert.equal(qualified.guardianSha256,sha(fs.readFileSync(root+'/guardian.lua')));assert.equal(fault.workerSha256,sha(fs.readFileSync(root+'/worker.lua')));assert.equal(fault.baseWorkerSha256,qualified.workerSha256);
const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));for(const name of ['backend.lua','conntrack-source.lua'])assert.equal(sha(fs.readFileSync(root+'/'+name)),previousConfig.files[name]);
"""+s[b:]
s=s.replace("const id='nss45-backend-'","const id='nss46-expiry-fault-'")
s=s.replace("normalized.files['backend.lua']=previousConfig.files['backend.lua'];","for(const name of ['worker.lua','guardian.lua'])normalized.files[name]=previousConfig.files[name];")
s=s.replace('Only initial recovery enumeration reuse and configuration binding may change','Only typed software expiry handling, test-only real observation delay and binding may change')
s=s.replace('initialRecoveryReadReuseTrial:true','realApplyExpiryFaultTrial:true')
emit('upgrade-fault.mjs',s)
for name,source in [('audit-fault.mjs','audit-backend-trial.mjs'),('verify-fault-rollback.mjs','verify-backend-rollback.mjs')]:
    body=(root/'work/nss45'/source).read_text().replace('work/nss45/backend-trial','work/nss46/expiry-fault').replace('backendOnlyTrial:true','realApplyExpiryFaultTrial:true')
    emit(name,body)
cfg=json.loads((root/'work/nss39/deployment-latest.json').read_text())
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-fault.mjs','audit-fault.mjs','verify-fault-rollback.mjs']:
    p=subprocess.run([node,'--check',str(here/name)],capture_output=True,text=True);assert p.returncode==0,p.stderr
unix=lambda p:'/mnt/'+p.resolve().as_posix()[0].lower()+p.resolve().as_posix()[2:]
rt=root/'work/nss9/lua-runtime/extracted/usr'
p=subprocess.run(['wsl.exe','-d','Athena-Cake-Build','--exec','/usr/bin/env','LD_LIBRARY_PATH='+unix(rt/'lib/x86_64-linux-gnu'),unix(rt/'bin/luac5.1'),'-p',unix(here/'fault-worker.lua')],capture_output=True,text=True);assert p.returncode==0,p.stderr
out={'passed':True,'workerSha256':sha(w.encode()),'baseWorkerSha256':sha((here/'stale-worker.lua').read_bytes()),'fakeFlow':False,'realWatchProducerAndLocksUnchanged':True,'realApplyAndRecoveryCLI':True,'oneDelayPerWorkerInstance':True,'allSourceAgeAndChildDeadlinesUnchanged':True,'querySourceUnchanged':True,'unknownErrorsRemainFatal':True,'nssEnabled':False,'independentRollbackSeconds':180,'stageExpirySeconds':480,'permanentRetentionAllowed':False,'scope':'Test-only finite real observation delay; real native reconciliation and exact recovery. No fabricated flow or game conclusion.'}
emit('fault-prepared.json',json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items()if 'Sha256'not in k}))
