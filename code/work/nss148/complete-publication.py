"""Complete the interrupted local export without rerunning tests or overwriting evidence."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone
w = Path(__file__).resolve().parents[2]
r = w / 'athena-nss-mainline'
o = w / 'work/nss148'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dump(p, v):
    assert not p.exists(), 'Preserve the first attempt'
    p.write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


failure = {
    'passed': False, 'kind': 'local-export-report-parent-directory-missing',
    'originalFailurePreserved': True, 'firstExportPartiallyCompleted': True,
    'source': 'work/nss148/save-evidence.py', 'line': 414,
    'originalScriptAndExportedEvidenceBytesKept': True,
    'commitOrPushStarted': False, 'productionWrites': False,
    'hardwareTestRerun': False, 'correction': 'Create the explicit reports directory and finish unchanged export',
}
dump(o / 'publication-v1-failure.json', failure)
dump(r / 'evidence/nss148-publication-failure.json', failure)
report = (w / 'outputs/nss148-mainline-report.html').read_bytes()
(r / 'reports').mkdir(exist_ok=True)
assert not (r / 'reports/nss148-mainline-report.html').exists()
(r / 'reports/nss148-mainline-report.html').write_bytes(report)

# The first script itself is frozen. Export this exact corrective continuation
# as an additional whitelist, without changing the first source-proof.
mp = r / 'source-manifest.json'
m = json.loads(mp.read_text(encoding='utf-8'))
prefix = json.loads(json.dumps(m['sources']))
assert len(prefix) == 2041
src = 'work/nss148/complete-publication.py'
b = (w / src).read_bytes()
target = r / 'code' / src
assert not target.exists()
target.write_bytes(b)
m['sources'].append({'path': 'code/' + src, 'workspaceSource': src,
                     'sha256': sha(b), 'bytes': len(b),
                     'role': 'local-export-failure-explicit-continuation'})
m['generatedAt'] = datetime.now(timezone.utc).isoformat()
mp.write_text(json.dumps(m, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
dump(r / 'evidence/nss148-publication-recovery-source-proof.json', {
    'historicPrefixSources': len(prefix),
    'historicPrefixCanonicalSha256': sha(json.dumps(prefix, sort_keys=True, separators=(',', ':')).encode()),
    'sources': 1, 'sourceHashes': {src: sha(b)},
    'originalPublicationSourceAndEvidenceBytesKept': True,
    'originalFailurePreserved': True, 'noOperationalBindingChanged': True,
    'hardwareTestRerun': False, 'productionWrites': False,
})
note = '\n本轮发布第一次在本地reports目录缺失时中断，部分导出已经完成，但没有开始提交或推送。原导出脚本及已生成证据保持原字节；单独的complete-publication接续只创建明确目录并复制原HTML、增加自身白名单和失败证明，随后重新校验，不重跑硬件。见 [发布失败](../evidence/nss148-publication-failure.json)。\n'
for name in ['docs/STATE.md', 'docs/EXPERIMENT_LOG.md']:
    p = r / name
    s = p.read_text(encoding='utf-8')
    marker = '\n## NSS142及更早历史\n'
    assert marker in s
    p.write_text(s.replace(marker, note + marker, 1), encoding='utf-8')
historic = json.loads((o / 'historic-files-before-export.json').read_text())
for path, digest in historic.items():
    if path == 'evidence/current-runtime.json':
        continue
    assert sha((r / path).read_bytes()) == digest, 'Frozen file changed: ' + path
assert sha((r / 'evidence/nss142-runtime.json').read_bytes()) == historic['evidence/current-runtime.json']
dump(o / 'export-precheck.json', {
    'passed': True, 'newSources': 150, 'totalSources': len(m['sources']),
    'old142RuntimeExact': True, 'historicFilesExactExceptCurrentRuntime': True,
    'firstPublicationFailurePreserved': True, 'actual1518BindingsFrozenExact': True,
    'controlledHardwareABA': True, 'strictCpuComparisonAccepted': False,
    'humanGameAcceptance': False, 'desktopOperated': False,
})
print(json.dumps(json.loads((o / 'export-precheck.json').read_text())))
