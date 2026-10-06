"""Verify the published v1 Git archive and exact preservation of prior evidence."""
from pathlib import Path
import argparse, subprocess, tarfile, io, json, hashlib

p = argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
workspace = Path(a.workspace).resolve()
output = Path(a.output).resolve()
base = 'bcf1ee62991ef0aa4f6133d64fc582b8f4054ed9'

def git(*args, text=False, data=None):
    return subprocess.check_output(['git', *args], cwd=repo, text=text, input=data)

def tree(ref):
    return {path.decode(): head.decode().split()[2]
            for item in git('ls-tree', '-r', '-z', ref, '--', 'code', 'evidence').split(b'\0') if item
            for head, path in [item.split(b'\t', 1)]}

assert not git('status', '--porcelain'), 'Working tree must be clean'
commit = git('rev-parse', 'HEAD', text=True).strip()
assert commit == git('ls-remote', 'origin', 'refs/heads/main', text=True).split()[0]
blob = git('archive', '--format=tar', commit)
dest = output / ('published-v1-' + commit[:12])
dest.mkdir()
with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
    archive.extractall(dest, filter='data')
check = subprocess.run(['C:/Users/lishu/AppData/Local/Programs/Python/Python312/python.exe', '-X', 'utf8',
                        str(dest / 'tools/check_repository.py')], capture_output=True, text=True, encoding='utf-8')
assert check.returncode == 0, check.stderr
checked = json.loads(check.stdout)
old, new = tree(base), tree(commit)
names = [path for path in old if path != 'evidence/current-runtime.json']
assert all(new.get(path) == old[path] for path in names)
data = git('cat-file', '--batch', data=('\n'.join(base + ':' + path for path in names) + '\n').encode())
offset = 0
for name in names:
    end = data.index(b'\n', offset)
    head = data[offset:end].split()
    assert head[1] == b'blob'
    size = int(head[2]); start = end + 1
    assert (dest / name).read_bytes() == data[start:start + size]
    assert data[start + size:start + size + 1] == b'\n'
    offset = start + size + 1
assert offset == len(data)
assert (dest / 'evidence/nss159-runtime.json').read_bytes() == git('show', base + ':evidence/current-runtime.json')
runtime = json.loads((dest / 'evidence/current-runtime.json').read_text(encoding='utf-8'))
assert runtime['round'] == 'NSS160' and runtime['noFurtherAutomaticExperiments']
assert runtime['coreFunctionalAcceptanceComplete'] and not runtime['v1FunctionalAcceptanceComplete']
assert runtime['humanSubjectiveAcceptance'] is None
manifest = json.loads((dest / 'source-manifest.json').read_text(encoding='utf-8'))
original = json.loads(git('show', base + ':source-manifest.json'))
assert manifest['sources'][:2753] == original['sources']
added = manifest['sources'][2753:]
for item in added:
    assert (dest / item['path']).read_bytes() == (workspace / item['workspaceSource']).read_bytes()
result = {'passed': True, 'commit': commit, 'remoteCommitMatched': True, 'actualGitArchiveChecked': True,
          'baseCommit': base, 'historicalGitBlobsRetained': len(names), 'old159RuntimeExactGitBytes': True,
          'newSourcesExactWorkspaceBytes': len(added), 'sourceHashesChecked': checked['sourceHashesChecked'],
          'filesChecked': checked['filesChecked'], 'markdownLinksChecked': checked['markdownLinksChecked'],
          'archiveSha256': hashlib.sha256(blob).hexdigest(), 'technicalMainlineFrozen': True,
          'humanSubjectiveAcceptance': None, 'fullV1HumanAcceptanceNotClaimed': True}
with (output / 'published-v1-git-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(result, f, indent=2); f.write('\n')
print(json.dumps(result))
