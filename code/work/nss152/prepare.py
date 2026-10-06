"""Reuse the tested lifecycle factory; isolate crash receipts in a new directory."""
from pathlib import Path
r=Path(__file__).resolve().parent;w=r.parents[1]
def put(n,s):
    p=r/n;assert not p.exists(),n
    p.write_text(s,encoding='utf-8',newline='')
for n in ['read-controlled.mjs','match-controlled.mjs','server.py','probe-peer.py','endpoint-firewall-guardian.py','client-watchdog.ps1','discover-peer.py','ssh-client.mjs','upload-server.py','upload-ack.mjs','bounded-pacer.mjs','health.mjs','read-final-physical.mjs']:
    s=(w/('work/nss151/'+n)).read_text(encoding='utf-8').replace('work/nss151/','work/nss152/').replace('NSS151_PASSIVE_READY','NSS152_PASSIVE_READY')
    put(n,s)
put('start-dallas.mjs',(w/'work/nss151/start-dallas-v3.mjs').read_text(encoding='utf-8').replace('work/nss151','work/nss152').replace("const unit='nss151-'","const unit='nss152-'"))
put('close-endpoint.mjs',(w/'work/nss151/close-endpoint-v4.mjs').read_text(encoding='utf-8').replace('work/nss151','work/nss152').replace('/^nss151-','/^nss152-'))
put('current-audit-diagnostic.mjs',(w/'work/nss151/current-audit-diagnostic-v5.mjs').read_text(encoding='utf-8').replace('./session-binding-v5.mjs','./session-binding.mjs').replace(r'work\/nss151',r'work\/nss152').replace('work/nss151/','work/nss152/'))
s=(w/'work/nss151/epoch-session-v5.mjs').read_text(encoding='utf-8').replace('./session-binding-v5.mjs','./session-binding.mjs').replace('work/nss151/','work/nss152/').replace('current-audit-diagnostic-v5.mjs','current-audit-diagnostic.mjs').replace('run-v5/continuity-private.json','run/continuity-private.json')
put('epoch-session.mjs',s)
# These exact helpers remain bound by the prior input set and support the audit.
for n in ['declared-baseline.mjs','failed-wan-owner.lua']:
    put(n,(w/('work/nss151/'+n)).read_text(encoding='utf-8'))
print('Crash test wrappers prepared; classifier, native factory, QoS and deadlines unchanged.')
