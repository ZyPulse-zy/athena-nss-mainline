"""Create one owned-flow-exit version; never mutate qualified historical inputs."""
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss154';native=r.parent/'nss149'
helpers=['start-dallas.mjs','match-controlled.mjs','read-controlled.mjs','current-audit-diagnostic.mjs','failed-wan-owner.lua','declared-baseline.mjs','ssh-client.mjs','bounded-pacer.mjs','upload-ack.mjs','upload-server.py','server.py','discover-peer.py','probe-peer.py','client-watchdog.ps1','endpoint-firewall-guardian.py','close-endpoint.mjs','crash-read.lua']
for name in helpers:
    p=r/name;assert not p.exists();p.write_text((old/name).read_text(encoding='utf-8').replace('work/nss154','work/nss155').replace('nss154-','nss155-').replace('NSS154_PASSIVE_READY','NSS155_PASSIVE_READY'),encoding='utf-8',newline='')
for name in ['module-stage.mjs','module-stage-guardian.lua','payload.mjs']:
    p=r/name;assert not p.exists();s=(native/name).read_text(encoding='utf-8')
    if name=='module-stage.mjs':
        s=s.replace("fs.readFileSync('work/nss149/fast-path.lua'","fs.readFileSync('work/nss155/fast-path.lua'")
        s=s.replace("fs.readFileSync('work/nss149/module-stage-guardian.lua'","fs.readFileSync('work/nss155/module-stage-guardian.lua'")
    if name=='payload.mjs':s=s.replace("'work/nss149/fast-path.lua'","'work/nss155/fast-path.lua'")
    if name=='module-stage-guardian.lua':
        anchor='record.automaticLifecycleEpochCompleted or record.classChangeTestCompleted or record.freshEpochRelearningCompleted';assert s.count(anchor)==1
        s=s.replace(anchor,anchor+' or record.flowEligibilityExitCompleted')
    p.write_text(s,encoding='utf-8',newline='')
print('New owned-flow-exit namespace created; historical factory and all frozen inputs unchanged.')
