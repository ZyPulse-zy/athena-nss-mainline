"""Read back the real pushed archive and compare history against original Git blobs.

The first verifier confused CRLF worktree bytes with original LF Git bytes.
Keep that failed source and result; use Git, not normalization, as the archive
identity authority. No router, application, or firewall operations.
"""
from pathlib import Path
import subprocess
import tarfile
import io
import hashlib
import json

w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
r = w / 'work/nss148'
base = '07d7a85a2630463013ef0cb1d6042bd0793f7176'


def git(*args, text=False, data=None):
    return subprocess.check_output(['git', *args], cwd=repo, text=text, input=data)


def tree(ref):
    b = git('ls-tree', '-r', '-z', ref, '--', 'code', 'evidence')
    return {path.decode(): head.decode().split()[2]
            for entry in b.split(b'\0') if entry
            for head, path in [entry.split(b'\t', 1)]}


commit = git('rev-parse', 'HEAD', text=True).strip()
remote = git('ls-remote', 'origin', 'refs/heads/main', text=True).split()[0]
assert remote == commit
blob = git('archive', '--format=tar', commit)
out = r / ('published-v2-' + commit[:12])
out.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
    archive.extractall(out, filter='data')
checked = subprocess.run([
    'C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe',
    str(out / 'tools/check_repository.py')], capture_output=True, text=True)
if checked.returncode:
    (r / 'failed-published-v2-checker.json').write_text(
        json.dumps({'code': checked.returncode, 'stdout': checked.stdout,
                    'stderr': checked.stderr}, indent=2) + '\n', encoding='utf-8')
    raise RuntimeError('Published archive checker failed; stop release chain')
proof = json.loads(checked.stdout)
previous = tree(base)
current = tree(commit)
names = [p for p in previous if p != 'evidence/current-runtime.json']
assert all(current.get(p) == previous[p] for p in names), 'Historical Git object changed'
data = git('cat-file', '--batch', data=('\n'.join(base + ':' + p for p in names) + '\n').encode())
offset = 0
for p in names:
    end = data.index(b'\n', offset)
    head = data[offset:end].split()
    assert len(head) == 3 and head[1] == b'blob', p
    n = int(head[2])
    start = end + 1
    original = data[start:start+n]
    assert (out / p).read_bytes() == original, p
    assert data[start+n:start+n+1] == b'\n'
    offset = start + n + 1
assert offset == len(data)
assert (out / 'evidence/nss142-runtime.json').read_bytes() == git('show', base + ':evidence/current-runtime.json')
for name in ['nss128-runtime.json', 'nss139-runtime.json', 'nss141-runtime.json', 'nss142-runtime.json']:
    assert (out / 'evidence' / name).read_bytes() == (repo / 'evidence' / name).read_bytes()
assert json.loads((out / 'evidence/current-runtime.json').read_text(encoding='utf-8'))['round'] == 'NSS148'
receipt = {
    'passed': True, 'commit': commit, 'remoteCommitMatched': True,
    'publishedGitArchiveChecked': True, 'sourceHashesChecked': proof['sourceHashesChecked'],
    'filesChecked': proof['filesChecked'], 'markdownLinksChecked': proof['markdownLinksChecked'],
    'baseCommit': base, 'historicalGitBlobsVerified': len(names),
    'old128139141142RuntimeExactBytesRetained': True,
    'allHistoricGitSourceAndEvidenceExceptCurrentRuntimeExact': True,
    'firstArchiveVerifierFailurePreserved': True,
    'archiveSha256': hashlib.sha256(blob).hexdigest(),
}
(r / 'published-git-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt))
