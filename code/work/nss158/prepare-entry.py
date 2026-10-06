"""Bind the same actual flow fixture and restoration to one finite ABA run."""
from pathlib import Path

root = Path(__file__).resolve().parent
prior = root.parent / 'nss157'

def put(name, text):
    with (root / name).open('x', encoding='utf-8', newline='') as f:
        f.write(text)

stage = (prior / 'module-stage-v4.mjs').read_text(encoding='utf-8')
for old, new in [("'./payload-v4.mjs'", "'./payload.mjs'"),
                 ('work/nss157/module-stage-guardian.lua', 'work/nss158/module-stage-guardian.lua'),
                 ('work/nss157/fast-path-v2.lua', 'work/nss158/fast-path.lua')]:
    assert stage.count(old) == 1, old
    stage = stage.replace(old, new)
put('module-stage.mjs', stage)

audit = (prior / 'current-audit-diagnostic.mjs').read_text(encoding='utf-8')
audit = audit.replace('work/nss157', 'work/nss158').replace('work\\/nss157', 'work\\/nss158')
put('current-audit-diagnostic.mjs', audit)
put('failed-wan-owner.lua', (prior / 'failed-wan-owner.lua').read_text(encoding='utf-8'))

driver = (prior / 'epoch-driver-live.mjs').read_text(encoding='utf-8')
for old, new in [("'./session-binding-live.mjs'", "'./session-binding.mjs'"),
                 ("'./module-stage-v4.mjs'", "'./module-stage.mjs'"),
                 ("const mode='epoch';assert.equal(typeof onDetached,'function');", "const mode='aba';assert.equal(expectedExit,false);assert.equal(typeof onDetached,'function');"),
                 ("/^work\\/nss157\\/pilot-(?:change|close)-\\d{14}-[a-f0-9]{16}\\/(?:successor-)?continuity-private\\.json$/", "/^work\\/nss158\\/pilot-aba-\\d{14}-[a-f0-9]{16}\\/continuity-private\\.json$/"),
                 ("const dir='work/nss157/automatic-epoch-'", "const dir='work/nss158/automatic-epoch-'"),
                 ('work/nss157/current-audit-diagnostic.mjs', 'work/nss158/current-audit-diagnostic.mjs')]:
    assert driver.count(old) >= 1, old
    driver = driver.replace(old, new)
start = driver.index('  if(expectedExit){')
end = driver.index('  for(const key of ', start)
driver = driver[:start] + driver[end:]
driver = driver.replace("['automaticLifecycleEpochCompleted','unchangedQoSPlan'", "['abaCompleted','unchangedQoSPlan'")
driver = driver.replace("assert.equal(latest.abaCompleted,false);", "assert.equal(latest.automaticLifecycleEpochCompleted,false);")
driver = driver.replace("['B']);for(const p of latest.phases)", "['A','B','A2']);for(const p of latest.phases)")
driver = driver.replace('automaticLifecycleEpoch:true,matchedForwardingABA:false', 'automaticLifecycleEpoch:false,matchedForwardingABA:true')
driver = driver.replace("mode:'epoch',controlledOwnerRequired", "mode:'aba',controlledOwnerRequired")
driver = driver.replace('matchedForwardingABARequested:false,matchedForwardingABACompleted:false', 'matchedForwardingABARequested:true,matchedForwardingABACompleted:completed&&failures.length===0')
driver = driver.replace('automaticLifecycleEpochCompleted:completed&&!expectedExit', 'automaticLifecycleEpochCompleted:false')
driver = driver.replace("mode:'epoch',output:dir", "mode:'aba',output:dir")
assert "assert.equal(latest.abaCompleted,false)" not in driver
put('epoch-driver.mjs', driver)

binding = (prior / 'session-binding-live.mjs').read_text(encoding='utf-8')
binding = binding.replace("'./session-binding-v8.mjs'", "'../nss157/session-binding-live.mjs'").replace('work/nss157/entry-qualified-live.json', 'work/nss158/entry-qualified.json')
put('session-binding.mjs', binding)
print('Prepared one ABA driver; original input reader/fixture/leases and exact retirement unchanged')
