from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys, uuid

w=Path(__file__).resolve().parents[1]
entry=w/'work/v45-early-acquisition'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
old=read(entry/'active-private.json')
assert old['state']=='RESTORED' and old['restorationPassed'] and not (entry/'active-lock').exists()
assert not (w/old['runtimeRoot']/'load-latest-private.json').exists()
model=read(w/read(entry/'entry-model-latest-private.json')['receipt'])
assert model['passed'] and model['sourceBindings']==3406 and len(model['checks'])==24
for rel,h in model['sourceHashes'].items():assert hashlib.sha256((w/rel).read_bytes()).hexdigest()==h
status_files=sorted(entry.glob('current-status-*-private.json'))
fresh=read(status_files[-1])['summary']
assert fresh['endpointConnectionPassed'] and fresh['entryState']=='RESTORED' and fresh['restorationPassed']
assert fresh['endpointReadonly']['ownedEndpointPortRows']==fresh['endpointReadonly']['v45UnitRows']==0
assert (datetime.now(timezone.utc)-datetime.fromisoformat(fresh['observedAt'])).total_seconds()<300
run=w/'work'/('v46-entry-resume-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8])
run.mkdir()
with (w/'work/v46-entry-resume-latest-private.json').open('x',encoding='utf8') as f:json.dump({'directory':run.relative_to(w).as_posix()},f)
with (run/'continuation-intent-private.json').open('x',encoding='utf8') as f:
    json.dump({'oldEntryResultUnchanged':True,'oldRuntimeRoot':old['runtimeRoot'],'oldLedger':old,
               'freshReadonlyEndpointCondition':fresh,'sameQualifiedEntrySourceHashes':model['sourceHashes'],
               'newFixtureRetryLoop':False,'singleContinuationAttempt':True,'desktopOperated':False},f,indent=2)
with (run/'stdout-private.txt').open('x',encoding='utf8') as log, (run/'stderr-private.txt').open('x',encoding='utf8') as err:
    p=subprocess.Popen(['C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
                        'work/v45-early-acquisition/entry.mjs','run'],cwd=w,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf8')
    for line in p.stdout:
        log.write(line);log.flush()
        try:
            data=json.loads(line)
            print(json.dumps({k:data[k] for k in ['step','passed','code','runtimeRoot','bindings','state','hardwareCompleted','restorationPassed','supervisorExitCode'] if k in data}),flush=True)
        except ValueError:print(json.dumps({'entryOutputRecordedLocally':True}),flush=True)
    code=p.wait()
with (run/'exit-private.json').open('x',encoding='utf8') as f:json.dump({'code':code,'singleContinuationAttempt':True},f)
print(json.dumps({'entryExitCode':code,'trackingDirectory':run.relative_to(w).as_posix()}),flush=True)
sys.exit(code)
