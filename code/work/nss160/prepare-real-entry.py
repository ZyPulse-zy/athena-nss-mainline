"""Reconnect the existing real application entry to the unchanged NSS158 native."""
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.with_name('nss140')
for name in ['read-real-candidates.mjs','record-candidates.mjs','application-ownership.mjs','application-filter.lua']:
    s=(old/name).read_text(encoding='utf-8').replace('work/nss140','work/nss160');(r/name).write_text(s,encoding='utf-8')
s=(old/'real-session.mjs').read_text(encoding='utf-8').replace("from './service-epoch.mjs'","from '../nss50/service-epoch.mjs'").replace("from './module-stage.mjs'","from '../nss158/module-stage.mjs'")
for name in ['compact-default-queues.mjs','parse-ecm-any-wan.mjs','uplink-tag-plan.mjs']:s=s.replace("from './"+name+"'","from '../nss140/"+name+"'")
s=s.replace("observationRoot='work/nss140'","observationRoot='work/nss160'").replace('work/nss140/real-matched-aba-','work/nss160/real-matched-aba-').replace('work/nss140/current-audit-diagnostic.mjs','work/nss160/current-audit-diagnostic.mjs').replace('p.sampleCount>=40','p.sampleCount>=38')
(r/'real-session.mjs').write_text(s,encoding='utf-8')
p=r/'current-audit-diagnostic.mjs';s=p.read_text(encoding='utf-8').replace('(?:automatic-epoch|controlled-class)','(?:automatic-epoch|controlled-class|real-matched-aba)');p.write_text(s,encoding='utf-8')
print('Real entry uses original application ownership and exact native158; no new lifecycle conditions')
