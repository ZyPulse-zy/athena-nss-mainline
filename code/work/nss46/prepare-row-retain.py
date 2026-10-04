"""Add only the previously proved row-overflow fix to the retained expiry version."""
from pathlib import Path
import hashlib,json,subprocess
here=Path(__file__).resolve().parent;root=here.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
def emit(name,s):(here/name).write_text(s,encoding='utf-8',newline='\n')
def run(name):
    r=subprocess.run(['C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-B','-X','utf8',str(here/name)],capture_output=True,text=True);print(r.stdout);assert r.returncode==0,r.stderr
s=(root/'work/nss45/build-row-candidate.py').read_text().replace('work/nss39/deployment-latest.json','work/nss46/deployment-latest.json')
s=s.replace("original=(root/'athena-nss-mainline/code/deployed-classifier'/name).read_bytes()","original=(root/dep['localDir']/name).read_bytes()")
emit('build-row.py',s);run('build-row.py')
emit('test-row.py',(root/'work/nss45/test-row-candidate.py').read_text());run('test-row.py')
s=(here/'test-expiry.py').read_text().replace("here/'stale-worker.lua'","here/'worker.lua'").replace("here/'stale-guardian.lua'","here/'guardian.lua'").replace('stale-qualified.json','combined-expiry-qualified.json').replace('stale-replay.lua','combined-expiry-replay.lua').replace('stale-replay-output.txt','combined-expiry-replay-output.txt')
emit('test-combined-expiry.py',s);run('test-combined-expiry.py')
# Exact row normalizer and real native query helper already tested with seven children.
assert (here/'conntrack-source.lua').read_bytes()==(root/'work/nss45/conntrack-source.lua').read_bytes()
def query(p):
    s=p.read_text();a=s.index('local function query(cmd,limit)');b=s.index('\nlocal AddressQuery=',a);return s[a:b]
assert query(here/'worker.lua')==query(root/'work/nss45/stale-worker.lua')
q=json.loads((here/'row-qualified.json').read_text());e=json.loads((here/'combined-expiry-qualified.json').read_text());assert q['passed']and q['checks']==48 and e['passed']and e['checks']==34
trial=here/'row-retain';trial.mkdir(exist_ok=True)
for name in ['worker.lua','guardian.lua','conntrack-source.lua']:(trial/name).write_bytes((here/name).read_bytes())
(trial/'backend.lua').write_bytes((root/'work/nss45/candidate-backend.lua').read_bytes())
s=(here/'upgrade-expiry.mjs').read_text().replace("root='work/nss46/expiry-retain'","root='work/nss46/row-retain'")
a=s.index('const qualified=');b=s.index("const id='nss46-expiry-'")
s=s[:a]+"""const qualified=JSON.parse(fs.readFileSync('work/nss46/row-qualified.json')),expiry=JSON.parse(fs.readFileSync('work/nss46/combined-expiry-qualified.json')),native=JSON.parse(fs.readFileSync('work/nss45/query-cleanup-native-qualified.json')),historical=JSON.parse(fs.readFileSync('work/nss45/row-trial/deployment-latest.json')),undoProof=JSON.parse(fs.readFileSync(historical.localDir+'/rollback-qualified.json'));assert.ok(qualified.passed&&qualified.checks===48&&expiry.passed&&expiry.checks===34&&native.passed&&native.checks===7&&undoProof.passed&&undoProof.automaticExpiryWithoutControllerRollback);for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(qualified.sources[name],sha(fs.readFileSync(root+'/'+name)));
const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));assert.equal(sha(fs.readFileSync(root+'/backend.lua')),previousConfig.files['backend.lua']);
"""+s[b:]
s=s.replace("const id='nss46-expiry-'","const id='nss46-row-'").replace("for(const name of ['worker.lua','guardian.lua'])normalized.files[name]=previousConfig.files[name];","for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])normalized.files[name]=previousConfig.files[name];")
s=s.replace('qualified typed software expiry handling and binding','qualified bounded row-overflow handling and binding').replace('qualifiedSoftwareExpiryRetention:true','qualifiedRowOverloadRetention:true')
emit('upgrade-row.mjs',s)
emit('audit-row.mjs',(here/'audit-expiry.mjs').read_text().replace('work/nss46/expiry-retain','work/nss46/row-retain').replace('qualifiedSoftwareExpiryRetention:true','qualifiedRowOverloadRetention:true'))
s=(here/'commit-expiry.mjs').read_text().replace('work/nss46/expiry-retain/deployment-latest.json','work/nss46/row-retain/deployment-latest.json')
a=s.index('const qualified=');b=s.index('const c=await connectRouter()',a)
s=s[:a]+"""const qualified=JSON.parse(fs.readFileSync('work/nss46/row-qualified.json')),expiry=JSON.parse(fs.readFileSync('work/nss46/combined-expiry-qualified.json')),historical=JSON.parse(fs.readFileSync('work/nss45/row-trial/deployment-latest.json')),undoProof=JSON.parse(fs.readFileSync(historical.localDir+'/rollback-qualified.json'));assert.ok(qualified.passed&&expiry.passed&&undoProof.passed&&undoProof.automaticExpiryWithoutControllerRollback);const cfg=JSON.parse(fs.readFileSync(ctx.localDir+'/config.json'));for(const name of ['worker.lua','guardian.lua','conntrack-source.lua'])assert.equal(qualified.sources[name],cfg.files[name]);
"""+s[b:]
s=s.replace('typedSoftwareExpiryRealChildQualified=true','boundedRowOverflowQualified=true')
emit('commit-row.mjs',s)
obs=(here/'observe-compact.mjs').read_text()
obs=obs.replace("const lua=String.raw`","const current=JSON.parse(fs.readFileSync('work/nss46/deployment-latest.json'));const ref=process.argv[3]??'work/nss46/deployment-latest.json';const wanted=JSON.parse(fs.readFileSync(ref)).configHash;\nconst lua=String.raw`")
needle='for i=1,35 do'
assert obs.count(needle)==1
obs=obs.replace(needle,"local due=now()+12;repeat local s=assert(j.parse(read('/tmp/router-project-game-classifier/classification.json',4194304)));local g=assert(j.parse(read('/tmp/router-project-game-classifier/guardian.json',8192)));if s.configSha256=='${wanted}'and s.status=='running'and g.healthy and g.producer==s.producer then break end;assert(now()<due,'Current instance startup not ready');n.nanosleep(0,100000000)until false\n"+needle)
emit('observe-current.mjs',obs)
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for name in ['upgrade-row.mjs','audit-row.mjs','commit-row.mjs','observe-current.mjs']:
    p=subprocess.run([node,'--check',str(here/name)],capture_output=True,text=True);assert p.returncode==0,p.stderr
emit('row-retain-prepared.json',json.dumps({'passed':True,'oneMajorVariable':'row-overflow handling','expiryAndBackendRetained':True,'localRowCases':48,'localCombinedExpiryCases':34,'sameSevenHistoricalRealQueryCasesReused':True,'nativeQueryHelperExactSha256':sha(query(here/'worker.lua').encode()),'normalizerExactNss45Sha256':sha((here/'conntrack-source.lua').read_bytes()),'checkpointAndIndependent180SecondRollback':True,'sourceAndDeadlineBoundsUnchanged':True,'nssEnabled':False},indent=2)+'\n')
print(json.dumps({'prepared':True,'localCases':82,'exactNativeQueryHelperUnchanged':True}))
