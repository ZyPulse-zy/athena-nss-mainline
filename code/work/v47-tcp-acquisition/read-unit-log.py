"""Resolve an empty sshd-tag lookup using the same bounded historical SSH unit window."""
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess
w=Path(__file__).resolve().parents[2];root=Path(__file__).resolve().parent
save=lambda p,x:p.open('x',encoding='utf8').write(json.dumps(x,indent=2)+'\n')
assert json.loads((root/'diagnostic-summary.json').read_text())['journalRows']==0
save(root/'unit-log-once-private.json',{'at':datetime.now(timezone.utc).isoformat(),'readonly':True,'reason':'Original sshd tag returned zero rows','sameHistoricalWindow':True})
code=r'''import json,subprocess,time
p=subprocess.run(['journalctl','--utc','--since','2026-10-07 10:30:35 UTC','--until','2026-10-07 10:31:20 UTC','-u','ssh.service','-u','sshd.service','--no-pager','-o','json','-n','128'],capture_output=True,text=True,timeout=8)
rows=[]
for line in p.stdout.splitlines():
 x=json.loads(line);rows.append({k:x[k] for k in ['__REALTIME_TIMESTAMP','SYSLOG_IDENTIFIER','SYSLOG_PID','MESSAGE'] if k in x})
print(json.dumps({'code':p.returncode,'stderr':p.stderr,'rows':rows,'serverNow':time.time()},ensure_ascii=True))
'''
quote=lambda s:"'"+s.replace("'","'\\''")+"'"
args=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=3','-o','ServerAliveCountMax=1','sub2api-dallas','python3 -B -E -s -u -c '+quote(code)]
began=datetime.now(timezone.utc).timestamp()
try:
 p=subprocess.run(args,cwd=w,capture_output=True,timeout=20)
 raw={'code':p.returncode,'stdout':p.stdout.decode('utf8','replace'),'stderr':p.stderr.decode('utf8','replace')}
except subprocess.TimeoutExpired as e:
 raw={'code':None,'timeout':True,'stdout':(e.stdout or b'').decode('utf8','replace'),'stderr':(e.stderr or b'').decode('utf8','replace')}
finished=datetime.now(timezone.utc).timestamp();save(root/'unit-log-raw-private.json',raw)
assert len(raw['stdout'].encode())+len(raw['stderr'].encode())<=65536
assert raw['code']==0,'Readonly unit-log SSH failed; raw result preserved'
x=json.loads(raw['stdout']);assert x['code']==0,'Readonly unit-log query failed; raw result preserved'
messages=[r.get('MESSAGE','') for r in x['rows']]
terms=['MaxStartups','drop connection','throttling','Accepted publickey','Connection closed','Connection reset','Disconnected','preauth','penalty','refused','timeout']
out={'passed':True,'readonly':True,'fixtureReopened':False,'sameHistoricalWindow':True,'journalRows':len(messages),
 'identifiers':sorted(set(r.get('SYSLOG_IDENTIFIER','') for r in x['rows'])),
 'logTermCounts':{s:sum(s.lower() in m.lower() for m in messages) for s in terms},
 'serverClockOffsetRangeSeconds':[x['serverNow']-finished,x['serverNow']-began]}
save(root/'unit-log-summary.json',out);print(json.dumps(out))
