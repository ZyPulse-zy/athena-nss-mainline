"""Prepare a fresh continuous controller candidate without changing the retained one."""
from pathlib import Path
import hashlib, json

root = Path(__file__).resolve().parent
w = root.parents[1]
old = w / 'work/resident-general-dev-i-20261008/endpoint-gate'
gate = root / 'endpoint-gate'
gate.mkdir()
names = ['Makefile', 'two_slot_predicate.h', 'predicate_test.c', 'rp_ecm_gate_lab_ct.c',
         'ecm_ae_classifier_public.h', 'control_harness.py', 'ct_harness.py', 'build_local.py']
provenance = {}
for name in names:
    raw = (old / name).read_bytes()
    provenance[name] = hashlib.sha256(raw).hexdigest()
    (gate / name).write_bytes(raw)

def once(s, before, after):
    assert s.count(before) == 1, before
    return s.replace(before, after)

c = (gate / 'rp_ecm_gate_lab_ct.c').read_text()
c = once(c, 'static bool diagnostic_only = true;',
    '/* Healthy qualified renewals extend residency; stale/terminal epochs never revive. */\n'
    'static bool continuous_residency;\nmodule_param(continuous_residency, bool, 0400);\n'
    'static bool diagnostic_only = true;')
c = once(c, ' WRITE_ONCE(classifier_until_ms, until);',
    ' if (continuous_residency) WRITE_ONCE(session_until_ms, ms + 120000);\n'
    ' WRITE_ONCE(classifier_until_ms, until);')
c = once(c, ' if (session_until_ms) {',
    ' if (continuous_residency && (!session_until_ms || diagnostic_only)) return -EINVAL;\n'
    ' if (session_until_ms) {')
c = c.replace('MODULE_VERSION("v16-three-exact-120s-DRAFT");',
    'MODULE_VERSION("resident-continuous-qualified-rolling-lease");')
(gate / 'rp_ecm_gate_lab_ct.c').write_text(c, newline='\n')

harness = (gate / 'control_harness.py').read_text()
harness = once(harness, 'static bool diagnostic_only, instance_valid;',
    'static bool continuous_residency;\\nstatic bool diagnostic_only, instance_valid;')
harness = once(harness, 'teardown=queue_failure=diagnostic_only=false;',
    'teardown=queue_failure=diagnostic_only=continuous_residency=false;')
extra = r'''\n for(unsigned mask=1;mask<8;mask++) {\n  reset();subset(mask);continuous_residency=true;session_until_ms=121000;\n  for(unsigned n=0;n<3;n++) if(mask&(1U<<n)) {check(drain_set("Y",&p[n])==0);check(permit_set("Y",&p[n])==0);}\n  for(unsigned step=1;step<=120;step++){\n   event_count=0;events[0]=0;set_time((1+3*step)*HZ);\n   check(renew_epoch(step,step+1,clock_ms+5000)==0);\n   check(session_until_ms==clock_ms+120000);\n   for(unsigned n=0;n<3;n++)check(lease_now(&slots[n])==((mask&(1U<<n))!=0));\n  }\n  u64 prior_session=session_until_ms;instance_valid=false;\n  check(renew_epoch(121,122,clock_ms+5500)==-ETIME);check(session_until_ms==prior_session);\n  instance_valid=true;set_time((classifier_until_ms/1000)*HZ);\n  check(renew_epoch(121,122,clock_ms+5000)==-ETIME);check(session_until_ms==prior_session);\n }\n'''
harness = once(harness, ' printf("subset extracted control checks passed:',
    extra + ' printf("subset extracted control checks passed:')
(gate / 'control_harness.py').write_text(harness, newline='\n')

runtime = (w / 'work/resident-general-dev-i-20261008/prepare-runtime.py').read_bytes()
(root / 'prepare-runtime.py').write_bytes(runtime)
service_old = w / 'work/resident-service-dev-i-20261008'
for name in ['storage.mjs', 'identity.mjs', 'service.ps1', 'service-launch.ps1', 'startup-health.mjs', 'daemon.mjs']:
    raw = (service_old / name).read_bytes()
    provenance['service/' + name] = hashlib.sha256(raw).hexdigest()
    text = raw.decode().replace('resident-service-dev-i-20261008', root.name)
    (root / name).write_text(text, newline='\n')
for name, digest in provenance.items():
    source = service_old / name[8:] if name.startswith('service/') else old / name
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
(root / 'origin-hashes-private.json').write_text(json.dumps(provenance, indent=2) + '\n')
print(json.dumps({'prepared': True, 'historicalSourcesUnchanged': True,
    'onlyNativeQualifiedRenewalAddsSlidingSession': True, 'productionWrites': False}))
