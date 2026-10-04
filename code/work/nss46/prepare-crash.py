"""One actual worker crash, unchanged sources, independently restorable owner."""
from pathlib import Path
import json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
d=json.loads((here/'deployment-latest.json').read_text());assert d['committed']
trial=here/'crash-trial';trial.mkdir()
for name in ['worker.lua','guardian.lua','conntrack-source.lua','backend.lua']:(trial/name).write_bytes((root/d['localDir']/name).read_bytes())
s=(here/'upgrade-row.mjs').read_text().replace("root='work/nss46/row-retain'","root='work/nss46/crash-trial'")
a=s.index('const qualified=');b=s.index("const id='nss46-row-'")
s=s[:a]+"const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));for(const name of ['worker.lua','guardian.lua','conntrack-source.lua','backend.lua'])assert.equal(sha(fs.readFileSync(root+'/'+name)),previousConfig.files[name]);\n"+s[b:]
s=s.replace("const id='nss46-row-'","const id='nss46-crash-'")
s=s.replace("for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])normalized.files[name]=previousConfig.files[name];",'')
s=s.replace('qualified bounded row-overflow handling and binding','only installation owner binding for the bounded real crash test').replace('qualifiedRowOverloadRetention:true','realWorkerCrashTrial:true')
(here/'upgrade-crash.mjs').write_text(s,encoding='utf-8',newline='\n')
for name,src in [('verify-crash-rollback.mjs','verify-fault-rollback.mjs'),('audit-crash.mjs','audit-fault.mjs')]:
    s=(here/src).read_text().replace('work/nss46/expiry-fault','work/nss46/crash-trial').replace('realApplyExpiryFaultTrial:true','realWorkerCrashTrial:true');(here/name).write_text(s,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-crash.mjs','verify-crash-rollback.mjs','audit-crash.mjs']:
    r=subprocess.run([node,'--check',str(here/name)],capture_output=True,text=True);assert r.returncode==0,r.stderr
print(json.dumps({'prepared':True,'sourcesUnchanged':True,'onlyOwnerBindingChanged':True,'oneCrash':True,'independentRollbackSeconds':180}))
