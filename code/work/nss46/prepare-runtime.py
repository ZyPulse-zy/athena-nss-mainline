"""Prepare sequential, independently reversible classifier changes."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def emit(name,s):
    (here/name).write_text(s,encoding='utf-8',newline='\n')
# Retain the already qualified recovery-only change before expiry testing.
trial=here/'backend-retain';trial.mkdir()
for name in ['worker.lua','guardian.lua','conntrack-source.lua']:
    (trial/name).write_bytes((root/'work/nss45'/('original-'+name)).read_bytes())
(trial/'backend.lua').write_bytes((root/'work/nss45/candidate-backend.lua').read_bytes())
s=(root/'work/nss45/upgrade-backend.mjs').read_text().replace("root='work/nss45/backend-trial'","root='work/nss46/backend-retain'").replace("const id='nss45-backend-'","const id='nss46-backend-'")
emit('upgrade-backend.mjs',s)
audit=(root/'work/nss45/audit-backend-trial.mjs').read_text().replace('work/nss45/backend-trial','work/nss46/backend-retain')
emit('audit-backend.mjs',audit)
obs=(root/'work/nss39/observe-compact.mjs').read_text().replace("out='work/nss39/'","out='work/nss46/'")
emit('observe-compact.mjs',obs)
commit=(root/'work/nss39/commit-channel.mjs').read_text().replace("path='work/nss39/deployment-latest.json'","path='work/nss46/backend-retain/deployment-latest.json'")
a=commit.index('const trial=');b=commit.index('const c=await connectRouter()',a)
commit=commit[:a]+"const qualified=JSON.parse(fs.readFileSync('work/nss45/recovery-qualified.json'));assert.ok(qualified.passed);const expiry=JSON.parse(fs.readFileSync('work/nss45/backend-trial/deployment-latest.json'));const undo=JSON.parse(fs.readFileSync(expiry.localDir+'/rollback-qualified.json'));assert.ok(undo.passed&&undo.automaticExpiryWithoutControllerRollback);assert.equal(qualified.results[1].sourceSha256,JSON.parse(fs.readFileSync(ctx.localDir+'/config.json')).files['backend.lua']);\n"+commit[b:]
commit=commit.replace('tcChildSupervisionQualified=true','initialRecoveryReuseQualified=true')
commit=commit.replace("ctx.commitAt=new Date().toISOString();","ctx.commitAt=new Date().toISOString();")
commit=commit.replace("await c.upload(ctx.localDir+'/cancel'", "fs.writeFileSync('work/nss46/deployment-latest.json',JSON.stringify(ctx,null,2)+'\\n');\n await c.upload(ctx.localDir+'/cancel'")
emit('commit-backend.mjs',commit)
# Expiry-only worker/guardian: the row-cap change remains a separate variable.
builder=(root/'work/nss45/build-stale-candidate.py').read_text()
builder=builder.replace("raw=(here/name).read_bytes();s=raw.decode()","raw=(root/'work/nss45'/('original-'+name)).read_bytes();s=raw.decode()")
builder=builder.replace("here=Path(__file__).resolve().parent","here=Path(__file__).resolve().parent;root=here.parents[1]")
builder=builder.replace("needle=\" if e.kind=='bounded-source-row-overflow'then return e.limit==2048 and e.observedRows==2049 end\"","needle=\" if e.kind=='bounded-source-overflow'then return e.stream=='stdout'and e.limit==524288 end\"")
builder=builder.replace('baseRowCandidateSha256','baseNss39Sha256').replace('Separate uninstalled variant of the row candidate.','Expiry-only change relative to NSS39; row handling unchanged.')
emit('build-expiry.py',builder)
subprocess.run(['C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-B','-X','utf8',str(here/'build-expiry.py')],check=True)
emit('test-expiry.py',(root/'work/nss45/test-stale-candidate.py').read_text())
# A test-only watch delay, once per instance, on a real admitted RT connection.
# It changes timing only. Parent/locks/request/flow identity and apply/recover CLI remain intact.
worker=(here/'stale-worker.lua').read_text()
needle='local overflowEpisode=false;local overflowRecovered=false;local overflowAttempts=0'
assert worker.count(needle)==1
worker=worker.replace(needle,"local faultDelayed=false\n"+needle)
needle="   atomic(ram..'/request.json',{version=23,boot=thisBoot,generation=cfg.generation,producer=producer,pid=me.pid,start=me.start,configSha256=configHash,snapshot=SoftwareRequest.project(snap)})"
assert worker.count(needle)==1
hook="""   if not faultDelayed and #SoftwareRequest.project(snap).flows>0 then
    faultDelayed=true;local began=snap.provenance.startedAtUptime
    io.stdout:write('NSS46_REAL_APPLY_DELAY_BEGIN sequence='..snap.provenance.sequence..'\\n');io.stdout:flush()
    local wait=math.max(0,began+6.10-now());n.nanosleep(math.floor(wait),math.floor(wait%1*1000000000))
    io.stdout:write('NSS46_REAL_APPLY_DELAY_END sequence='..snap.provenance.sequence..' age='..(now()-began)..'\\n');io.stdout:flush()
   end
"""
worker=worker.replace(needle,hook+needle)
emit('fault-worker.lua',worker)
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-backend.mjs','audit-backend.mjs','observe-compact.mjs','commit-backend.mjs']:
    p=subprocess.run([node,'--check',str(here/name)],capture_output=True,text=True);assert p.returncode==0,p.stderr
emit('prepared.json',json.dumps({'passed':True,'backendAlreadyQualified':True,'expiryOnly':True,'testFaultChangesOnlyRealObservationTiming':True,'fakeFlowGenerated':False,'expirySeconds':6,'mutationSeconds':6,'sourceRows':2048,'nssEnabled':False,'codeHashes':{p.name:sha(p.read_bytes())for p in here.iterdir()if p.suffix in ['.py','.mjs','.lua']}},indent=2)+'\n')
print(json.dumps({'prepared':True,'backendRetainThenRealExpiryFault':True,'nssEnabled':False}))
