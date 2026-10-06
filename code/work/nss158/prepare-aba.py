"""Restore the proven 20-second software/NSS/software observer around NSS157."""
from pathlib import Path

root = Path(__file__).resolve().parent
prior = root.parent / 'nss157'
source = (prior / 'fast-path-v2.lua').read_text(encoding='utf-8')

def once(old, new):
    global source
    assert source.count(old) == 1, old
    source = source.replace(old, new)

once(' local function measure()\n  assert(now()<R.deadline-55,',
     " local function measure(name)\n  assert(now()<R.deadline-(name=='A'and 78 or name=='B'and 55 or 28),")
once("local p={name='B',requestedSeconds=20", "local p={name=name,requestedSeconds=20")
once("local s=tick('B');if not s then", "local s=tick(name);if not s then")
once('R.lifecycleVersion=157;', 'R.abaVersion=158;')
once("   tick('CLOSED');G('tagsBeforeLearning',I)",
     "  R.qosAtA=qos.snapshot();measure('A');G('tagsAfterA',I)")
once('R.qosAccelerated=qos.snapshot();measure()', "R.qosAccelerated=qos.snapshot();measure('B')")
once("  G('tagsAfterLifecycle',I);tick('CLOSED')\n   F();",
     "  G('tagsBeforeA2',I);measure('A2');G('tagsAfterA2',I)\n  R.qosAfterA2=qos.snapshot();F();")
once('R.fastPathEpochCompleted=true;R.abaCompleted=false;R.automaticLifecycleEpochCompleted=true',
     'R.fastPathEpochCompleted=true;R.abaCompleted=true;R.automaticLifecycleEpochCompleted=false')
once('stableSeconds=R.phases[1].seconds,startedAt=R.phases[1].startedAt,lastStableAt=R.phases[1].endedAt',
     'stableSeconds=R.phases[2].seconds,startedAt=R.phases[2].startedAt,lastStableAt=R.phases[2].endedAt')

def section(text, a, b):
    start = text.index(a)
    return text[start:text.index(b, start)]

original = (prior / 'fast-path-v2.lua').read_text(encoding='utf-8')
for a, b in [(' local function observe()', ' local function counters('),
             (' retire=function(C)', ' local function tick('),
             (' local function tick(name)', ' local function measure('),
             (' function out.align(deadline)', ' function out.run(')]:
    assert section(original, a, b) == section(source, a, b), a
with (root / 'fast-path.lua').open('x', encoding='utf-8', newline='') as f:
    f.write(source)

guardian = (prior / 'module-stage-guardian.lua').read_text(encoding='utf-8')
condition = 'if record.automaticLifecycleEpochCompleted or record.classChangeTestCompleted'
assert guardian.count(condition) == 1
guardian = guardian.replace(condition, 'if record.abaCompleted or record.automaticLifecycleEpochCompleted or record.classChangeTestCompleted')
with (root / 'module-stage-guardian.lua').open('x', encoding='utf-8', newline='') as f:
    f.write(guardian)

payload = (prior / 'payload-v4.mjs').read_text(encoding='utf-8')
assert payload.count('work/nss157/fast-path-v2.lua') == 1
payload = payload.replace('work/nss157/fast-path-v2.lua', 'work/nss158/fast-path.lua')
with (root / 'payload.mjs').open('x', encoding='utf-8', newline='') as f:
    f.write(payload)
print('Prepared offline ABA candidate; precise retirement and classifier unchanged')
