"""Local publication check for the completed continuous-qualified-residency milestone."""
from pathlib import Path
import argparse, datetime, hashlib, io, json, subprocess, sys, tarfile, uuid

p = argparse.ArgumentParser()
p.add_argument('mode', choices=['stage', 'archive'])
p.add_argument('--output')
a = p.parse_args()
w = Path(__file__).resolve().parents[2]
repo = w / 'athena-nss-mainline'
base = '78c10db6f8220d1925081bd5252ab2f021b31900'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=repo)

def emit(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def blob_batch(specs):
    data = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=repo,
        input=('\n'.join(specs) + '\n').encode())
    pos = 0
    for spec in specs:
        end = data.index(b'\n', pos)
        head = data[pos:end].split()
        assert head[1] == b'blob', spec
        size = int(head[2])
        start = end + 1
        yield data[start:start+size]
        assert data[start+size:start+size+1] == b'\n'
        pos = start + size + 1
    assert pos == len(data)

def tree(ref):
    result = {}
    for row in git('ls-tree', '-r', '-z', ref, '--', 'code', 'evidence').split(b'\0'):
        if row:
            head, name = row.split(b'\t', 1)
            result[name.decode()] = head.split()[2].decode()
    return result

out = Path(a.output).resolve() if a.output else w / 'work' / (
    'resident-continuous-publication-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
    + '-' + uuid.uuid4().hex[:8])
if a.mode == 'stage':
    out.mkdir(parents=True, exist_ok=False)
else:
    assert a.output and out.is_dir()

try:
    original = json.loads(git('show', base + ':source-manifest.json'))
    manifest = json.loads((repo / 'source-manifest.json').read_text(encoding='utf-8'))
    evidence = json.loads((repo / 'evidence/resident-continuous.json').read_text(encoding='utf-8'))
    n = len(original['sources'])
    assert n == 6257 and manifest['sources'][:n] == original['sources']
    fresh = manifest['sources'][n:]
    assert fresh and len(manifest['sources']) == n + len(fresh)
    assert evidence['actualIntegration']['completed'] and evidence['actualIntegration']['nssSeconds'] >= 190
    assert evidence['actualIntegration']['retainedSamplesEcm1'] and evidence['restoration']['ecmClosedAndZero']
    assert len(evidence['sourceHashes']) == len(fresh)
    for item in fresh:
        assert item['path'] == 'code/' + item['workspaceSource']
        raw = (w / item['workspaceSource']).read_bytes()
        assert raw == (repo / item['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item['sha256'] == evidence['sourceHashes'][item['workspaceSource']]
    fixed = ['.gitattributes', 'AGENTS.md', 'README.md', 'docs/EXPERIMENT_LOG.md',
        'docs/KNOWN_FAILURES.md', 'docs/PLAN.md', 'docs/RESIDENT_NORMAL_CONTROLLER.md',
        'docs/RESIDENT_SERVICE.md', 'docs/STATE.md', 'source-manifest.json',
        'evidence/resident-continuous.json', 'docs/RESIDENT_CONTINUOUS.md',
        'tools/check_resident_continuous.py', 'tools/check_repository.py']
    allowed = set(fixed + [item['path'] for item in fresh])
    assert len(allowed) == len(fixed) + len(fresh)
    if a.mode == 'stage':
        assert git('rev-parse', 'HEAD').decode().strip() == base
        assert git('branch', '--show-current').decode().strip() == 'main'
        assert not git('diff', '--cached', '--name-only')
        rows = [r for r in git('status', '--porcelain=v1', '-z', '--untracked-files=all').split(b'\0') if r]
        changed = {r[3:].decode() for r in rows}
        assert changed == allowed, 'Working-tree changes differ from the curated allowlist'
        for row in rows:
            assert row[:2] in (b' M', b'??')
        add = subprocess.run(['git', 'add', '--', *sorted(allowed)], cwd=repo,
            capture_output=True, text=True, encoding='utf-8')
        emit(out / 'stage-add-output.json', {'code': add.returncode, 'stdout': add.stdout, 'stderr': add.stderr})
        assert add.returncode == 0
        staged = set(git('diff', '--cached', '--name-only', '-z').decode().strip('\0').split('\0'))
        assert staged == allowed
        check = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=repo,
            capture_output=True, text=True, encoding='utf-8')
        emit(out / 'stage-whitespace-check.json', {'code': check.returncode, 'stdout': check.stdout, 'stderr': check.stderr})
        assert check.returncode == 0
        for item, raw in zip(fresh, blob_batch([':' + item['path'] for item in fresh])):
            assert raw == (w / item['workspaceSource']).read_bytes(), item['path']
        index_tree = git('write-tree').decode().strip()
        old, new = tree(base), tree(index_tree)
        assert all(new.get(name) == digest for name, digest in old.items())
        receipt = {'passed': True, 'baseCommit': base, 'reviewedIndexTree': index_tree,
            'stagedFiles': len(staged), 'newSourceBytesVerified': len(fresh),
            'historicalCodeEvidenceBlobsPreserved': len(old), 'whitespaceCheckPassed': True,
            'hardwareIntegrationCompleted': True, 'outputDirectory': str(out)}
        emit(out / 'stage-receipt.json', receipt)
    else:
        stage = json.loads((out / 'stage-receipt.json').read_text(encoding='utf-8'))
        assert stage['passed'] and not git('status', '--porcelain')
        commit = git('rev-parse', 'HEAD').decode().strip()
        assert git('rev-parse', 'HEAD^{tree}').decode().strip() == stage['reviewedIndexTree']
        assert commit == git('ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
        archive = git('archive', '--format=tar', commit)
        archive_path = out / 'published-tree.tar'
        with archive_path.open('xb') as f:
            f.write(archive)
        dest = out / ('published-tree-' + commit[:12])
        dest.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
            tf.extractall(dest, filter='data')
        check = subprocess.run([sys.executable, '-X', 'utf8', str(dest / 'tools/check_repository.py')],
            cwd=dest, capture_output=True, text=True, encoding='utf-8')
        emit(out / 'archive-checker-output.json', {'code': check.returncode, 'stdout': check.stdout, 'stderr': check.stderr})
        assert check.returncode == 0, check.stderr
        checked = json.loads(check.stdout)
        old, new = tree(base), tree(commit)
        assert all(new.get(name) == digest for name, digest in old.items())
        names = list(old)
        for name, raw in zip(names, blob_batch([base + ':' + name for name in names])):
            assert (dest / name).read_bytes() == raw, name
        archived_manifest = json.loads((dest / 'source-manifest.json').read_text(encoding='utf-8'))
        assert archived_manifest == manifest
        assert json.loads((dest / 'evidence/resident-continuous.json').read_text(encoding='utf-8')) == evidence
        for item in fresh:
            assert (dest / item['path']).read_bytes() == (w / item['workspaceSource']).read_bytes()
        receipt = {'passed': True, 'commit': commit, 'remoteCommitMatched': True,
            'actualGitArchiveChecked': True, 'baseCommit': base,
            'historicalCodeEvidenceBlobsPreserved': len(old), 'historicalManifestPrefixPreserved': n,
            'newSourcesExactWorkspaceBytes': len(fresh), 'sourceHashesChecked': checked['sourceHashesChecked'],
            'filesChecked': checked['filesChecked'], 'markdownLinksChecked': checked['markdownLinksChecked'],
            'archiveSha256': hashlib.sha256(archive).hexdigest(),
            'hardwareIntegrationCompleted': True, 'uninterruptedPermanentNssClaim': False,
            'outputDirectory': str(out)}
        emit(out / 'publication-receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False))
except Exception as error:
    emit(out / (a.mode + '-failure.json'), {'passed': False, 'errorType': type(error).__name__, 'error': str(error)})
    raise
