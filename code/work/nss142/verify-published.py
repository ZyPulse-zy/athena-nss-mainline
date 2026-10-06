"""Verify the pushed morning closure from an actual Git archive."""
from pathlib import Path
import subprocess, tarfile, io, hashlib, json
w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
r = w / 'work/nss142'
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=repo, text=True).split()[0]
assert remote == commit
blob = subprocess.check_output(['git', 'archive', '--format=tar', commit], cwd=repo)
out = r / ('published-' + commit[:12])
out.mkdir(exist_ok=False)
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
    archive.extractall(out, filter='data')
p = subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe', str(out / 'tools/check_repository.py')], capture_output=True, text=True)
if p.returncode:
    (r / 'failed-published-checker.json').write_text(json.dumps({'code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}, indent=2) + '\n')
    raise RuntimeError('Published archive checker failed; stop release chain')
proof = json.loads(p.stdout)
for name in ['nss128-runtime.json', 'nss139-runtime.json', 'nss141-runtime.json']:
    assert (out / 'evidence' / name).read_bytes() == (repo / 'evidence' / name).read_bytes()
assert json.loads((out / 'evidence/current-runtime.json').read_text())['round'] == 'NSS142'
receipt = {'passed': True, 'commit': commit, 'remoteCommitMatched': True, 'publishedGitArchiveChecked': True,
           'sourceHashesChecked': proof['sourceHashesChecked'], 'filesChecked': proof['filesChecked'],
           'markdownLinksChecked': proof['markdownLinksChecked'], 'old128139141RuntimeExactBytesRetained': True,
           'archiveSha256': hashlib.sha256(blob).hexdigest()}
(r / 'published-git-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
