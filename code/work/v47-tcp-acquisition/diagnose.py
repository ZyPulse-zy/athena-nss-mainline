"""Bounded reads of frozen v46 startup evidence and existing endpoint SSH logs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys

w = Path(__file__).resolve().parents[2]
root = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
save = lambda p, v: p.open('x', encoding='utf8').write(json.dumps(v, indent=2) + '\n')
assert not (root/'diagnostic-once-private.json').exists(), 'Diagnostic already consumed'
active = read(w/'work/v45-early-acquisition/active-private.json')
assert active['state'] == 'RESTORED' and active['restorationPassed']
assert not (w/'work/v45-early-acquisition/active-lock').exists()
runtime = w/active['runtimeRoot']
assert active['runtimeRoot'] == 'work/v45-run-20261007103021-bfd051fe'
load = read(runtime/'load-latest-private.json')
load_dir = w/load['dir']
samples = [json.loads(x) for x in (load_dir/'load-samples-private.jsonl').read_text(encoding='utf8').splitlines()]
result = read(load_dir/'result-private.json')
events = []; prior = {}
for row in samples:
    if row.get('event'):
        events.append({k:row[k] for k in ['event','at','slot','attempt','reason'] if k in row})
        continue
    for child in row.get('tcpChildren', []):
        key = child['slot']; state = (child.get('attempt'), child.get('connected'))
        if prior.get(key) != state:
            events.append({'event':'stateChange','at':row['at'],'elapsed':row['elapsed'],
                           **{k:child[k] for k in ['slot','attempt','connected','spawnedAt','bytes'] if k in child}})
            prior[key] = state
first = next(x for x in samples if x.get('tcpConnected'))
summary = {'readonly':True,'fixtureReopened':False,'nssStarted':False,
           'firstAllPayloadSeconds':first['elapsed'],'seconds':result['seconds'],
           'finalErrors':result['errors'],'events':events,
           'frozenEvidenceSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in [load_dir/'load-samples-private.jsonl',load_dir/'result-private.json']}}
save(root/'frozen-acquisition-analysis.json', summary)
save(root/'diagnostic-once-private.json', {'at':datetime.now(timezone.utc).isoformat(),
    'readonly':True,'previousState':'RESTORED','noFixtureOrNssWrites':True,
    'priorLocalQueryFailuresRetained':[
        {'command':'git status --short from workspace root','error':'fatal: not a git repository','corrected':'Use athena-nss-mainline as cwd'},
        {'command':'Get-Content ssh-download-sender.py','error':'path not found','corrected':'Actual sender is download-server.py'}]})
remote = r'''import json,subprocess
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=8)
 return {'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
j=run(['journalctl','--utc','--since','2026-10-07 10:30:35 UTC','--until','2026-10-07 10:31:20 UTC','-t','sshd','--no-pager','-o','json','-n','128'])
rows=[]
if j['code']==0:
 for line in j['stdout'].splitlines():
  x=json.loads(line);rows.append({k:x[k] for k in ['__REALTIME_TIMESTAMP','SYSLOG_PID','MESSAGE'] if k in x})
policy=run(['/usr/sbin/sshd','-T'])
print(json.dumps({'journalCode':j['code'],'journalStderr':j['stderr'],'journalRows':rows,'policy':policy},ensure_ascii=True))
'''
quote = lambda s: "'" + s.replace("'", "'\\''") + "'"
command = ['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8',
           '-o','ServerAliveInterval=3','-o','ServerAliveCountMax=1','sub2api-dallas',
           'python3 -B -E -s -u -c '+quote(remote)]
started = datetime.now(timezone.utc)
try:
    p = subprocess.run(command, cwd=w, capture_output=True, timeout=25)
    raw = {'code':p.returncode,'stdout':p.stdout.decode('utf8','replace'),
           'stderr':p.stderr.decode('utf8','replace'),'seconds':(datetime.now(timezone.utc)-started).total_seconds()}
except subprocess.TimeoutExpired as e:
    raw = {'code':None,'timeout':True,'stdout':(e.stdout or b'').decode('utf8','replace'),
           'stderr':(e.stderr or b'').decode('utf8','replace')}
save(root/'endpoint-ssh-log-raw-private.json', raw)
assert len(raw['stdout'].encode())+len(raw['stderr'].encode()) <= 65536, 'Readonly output ceiling exceeded'
assert raw['code']==0, 'Readonly endpoint SSH diagnostic failed; original output preserved'
data = json.loads(raw['stdout'])
assert data['journalCode']==0 and data['policy']['code']==0, 'Readonly journal/policy failed; original output preserved'
messages = [x.get('MESSAGE','') for x in data['journalRows']]
terms = ['MaxStartups','drop connection','throttling','Connection closed','Accepted publickey',
         'Connection reset','Disconnected','preauth','penalty','refused','timeout']
out = {'passed':True,'readonly':True,'fixtureReopened':False,'nssStarted':False,
       'frozenTimelineEvents':len(events),'firstAllPayloadSeconds':first['elapsed'],
       'finalErrors':result['errors'],'journalRows':len(messages),
       'logTermCounts':{term:sum(term.lower() in s.lower() for s in messages) for term in terms},
       'sshAcquisitionPolicy':{s.split()[0]:' '.join(s.split()[1:]) for s in data['policy']['stdout'].splitlines()
                               if s.split()[0] in ['maxstartups','persourcemaxstartups','persourcenetblocksize','persourcepenalties','logingracetime','maxsessions']}}
save(root/'diagnostic-summary.json',out)
print(json.dumps(out))
