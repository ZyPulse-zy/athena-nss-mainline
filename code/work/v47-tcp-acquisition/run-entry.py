"""One explicit, unchanged v45 entry trial after bounded v46 SSH phase diagnosis."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys

w=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
save=lambda p,x:p.open('x',encoding='utf8').write(json.dumps(x,indent=2)+'\n')
entry=w/'work/v45-early-acquisition';active=read(entry/'active-private.json')
assert active['state']=='RESTORED' and active['restorationPassed'] and not (entry/'active-lock').exists()
assert active['runtimeRoot']=='work/v45-run-20261007103021-bfd051fe'
assert read(root/'unit-log-summary.json')['passed']
model=read(w/read(entry/'entry-model-latest-private.json')['receipt'])
assert model['passed'] and model['sourceBindings']==3406 and len(model['checks'])==24
for p,h in model['sourceHashes'].items():assert hashlib.sha256((w/p).read_bytes()).hexdigest()==h
save(root/'entry-attempt-once-private.json',{'at':datetime.now(timezone.utc).isoformat(),'explicitUserContinue':True,
    'singleAttempt':True,'previousRuntime':active['runtimeRoot'],'sameSourceHashes':model['sourceHashes'],
    'sshPreauthenticationObservationNotRootCauseProof':True,'fixtureLimitsUnchanged':True,
    'noCoreOrCpuOrGameRetest':True,'residentNssNotStarted':True})
remote=r'''import json,subprocess
p=subprocess.run(['ss','-H','-lntup'],capture_output=True,text=True,timeout=5)
q=subprocess.run(['systemctl','list-units','--all','--no-legend','v45-run-*'],capture_output=True,text=True,timeout=5)
assert p.returncode==q.returncode==0
ports=sum(':45817 ' in s or ':45818 ' in s for s in p.stdout.splitlines())
units=len(q.stdout.strip().splitlines()) if q.stdout.strip() else 0
assert ports==units==0
print(json.dumps({'passed':True,'readonly':True,'ownedEndpointPortRows':ports,'ownedEntryUnitRows':units}))
'''
quote=lambda s:"'"+s.replace("'","'\\''")+"'"
try:
 p=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=3','-o','ServerAliveCountMax=1','sub2api-dallas','python3 -B -E -s -u -c '+quote(remote)],cwd=w,capture_output=True,timeout=20)
except subprocess.TimeoutExpired as e:
 save(root/'entry-preflight-raw-private.json',{'code':None,'timeout':True,'stdout':(e.stdout or b'').decode('utf8','replace'),'stderr':(e.stderr or b'').decode('utf8','replace')})
 raise
save(root/'entry-preflight-raw-private.json',{'code':p.returncode,'stdout':p.stdout.decode('utf8','replace'),'stderr':p.stderr.decode('utf8','replace')})
assert p.returncode==0,'Read-only endpoint preflight refused; no fixture started'
fresh=json.loads(p.stdout);assert fresh['passed']
print(json.dumps({'step':'endpoint-readonly-preflight','passed':True,'ownedEndpointPortRows':0,'ownedEntryUnitRows':0}),flush=True)
with (root/'entry-stdout-private.txt').open('x',encoding='utf8') as log,(root/'entry-stderr-private.txt').open('x',encoding='utf8') as err:
 p=subprocess.Popen(['C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',
                     'work/v45-early-acquisition/entry.mjs','run'],cwd=w,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf8')
 for line in p.stdout:
  log.write(line);log.flush()
  try:
   x=json.loads(line)
   print(json.dumps({k:x[k] for k in ['step','passed','code','runtimeRoot','bindings','state','hardwareCompleted','restorationPassed','supervisorExitCode'] if k in x}),flush=True)
  except ValueError:print(json.dumps({'entryOutputPreservedLocally':True}),flush=True)
 code=p.wait()
save(root/'entry-exit-private.json',{'code':code,'singleAttemptOnly':True})
print(json.dumps({'entryExitCode':code,'trackingDirectory':root.relative_to(w).as_posix()}),flush=True)
sys.exit(code)
