"""One UDP-gap attempt using unchanged NSS159/158 runtime and finite passive reads."""
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.with_name('nss159')
for name in ['download-client.mjs','download-server.py','download-policy.mjs','owned-load-policy.mjs','match-controlled.mjs','read-controlled.mjs','start-dallas.mjs','close-endpoint-v2.mjs','failed-wan-owner.lua','receiver.py','server.py','endpoint-firewall-guardian.py','discover-peer.py','probe-peer.py','client-watchdog.ps1']:
    s=(old/name).read_text(encoding='utf-8');s=s.replace('work/nss159','work/nss160').replace('nss159-','nss160-');(r/name).write_text(s,encoding='utf-8')
s=(old/'current-audit-diagnostic-v4.mjs').read_text(encoding='utf-8').replace('./session-binding-v4.mjs','./session-binding.mjs').replace("from '../nss140/service-epoch.mjs'","from '../nss50/service-epoch.mjs'").replace("from '../nss140/declared-baseline.mjs'","from './declared-baseline.mjs'").replace('work/nss159','work/nss160').replace('nss159\\/','nss160\\/').replace('fourHealthyWanBaseline:true','allFiveHealthyWanBaseline:true').replace('failedUnselectedWan4ProcessEpochMayChange:true','failedUnselectedWan4ProcessEpochMayChange:false')
(r/'current-audit-diagnostic.mjs').write_text(s,encoding='utf-8')
s=(old/'epoch-driver-v4.mjs').read_text(encoding='utf-8').replace('./session-binding-v4.mjs','./session-binding.mjs').replace("from '../nss140/declared-baseline.mjs'","from './declared-baseline.mjs'").replace("from '../nss140/service-epoch.mjs'","from '../nss50/service-epoch.mjs'").replace('work/nss159','work/nss160').replace('nss159\\/','nss160\\/').replace('current-audit-diagnostic-v4.mjs','current-audit-diagnostic.mjs')
(r/'epoch-driver.mjs').write_text(s,encoding='utf-8')
s=(old/'pilot-supervisor-v4.mjs').read_text(encoding='utf-8').replace('./session-binding-v4.mjs','./session-binding.mjs').replace('./epoch-driver-v4.mjs','./epoch-driver.mjs').replace('work/nss159','work/nss160').replace('current-audit-diagnostic-v4.mjs','current-audit-diagnostic.mjs').replace("assert.ok(Date.now()<Date.parse('2026-10-06T11:30:00Z'),'Evening restoration margin unavailable');","// Direct renewed user authorization; inherited 180/210/250-second deadlines unchanged.")
s=s.replace("import {requireOwnedDownload} from './owned-load-policy.mjs';","import {requireOwnedDownload} from './owned-load-policy.mjs';\nimport {startCapturePair} from './capture-pair.mjs';")
s=s.replace('const events=[];let started=false;','const events=[];let started=false,captureDone;')
s=s.replace("save('lifetime-before-aba',lifetime);","captureDone=await startCapturePair(load,config);\n save('lifetime-before-aba',lifetime);")
s=s.replace("const result=read(trial.output,'result'),record=read(trial.output,'last-record-private');","const result=read(trial.output,'result'),record=read(trial.output,'last-record-private');\n save('wire-summary',await captureDone());")
s=s.replace('NSS159 finite controlled DOWNLOAD ABA','v1 sole bounded UDP-gap investigation')
(r/'pilot-supervisor.mjs').write_text(s,encoding='utf-8')
print('Prepared only finite gap test; native, firmware gate, QoS and classifier unchanged')
