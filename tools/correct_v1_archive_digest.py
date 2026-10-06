"""Append a Git-byte digest correction; preserve original observations and failure."""
from pathlib import Path
import json, hashlib, subprocess

repo = Path(__file__).resolve().parents[1]
w = repo.parent
r = w / 'work/nss160'
base = 'bcf1ee62991ef0aa4f6133d64fc582b8f4054ed9'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
failed_archive = r / ('published-v1-' + commit[:12])
relative = 'evidence/nss128-comparison.json'
original_meta = read(repo / 'evidence/nss160-historical-cpu-reuse.json')
actual = subprocess.check_output(['git', 'show', base + ':' + relative], cwd=repo)
working = (repo / relative).read_bytes()
assert (failed_archive / relative).read_bytes() == actual
assert sha(working) == original_meta['historicalEvidenceSha256'] != sha(actual)
assert working.replace(b'\r\n', b'\n') == actual
assert json.loads(working) == json.loads(actual)
failure = {'passed': False, 'stage': 'actual Git archive checker', 'commit': commit,
           'exitCode': 1, 'originalAssertion': "cpu160['historicalEvidenceSha256']==hashlib.sha256((root/cpu160['historicalEvidenceReused']).read_bytes()).hexdigest()",
           'commitChainStoppedAfterFailedArchive': True, 'failedArchiveRetainedLocally': True,
           'experimentOrCpuMetricChanged': False}
correction = {'passed': True, 'appliesTo': ['evidence/nss160-historical-cpu-reuse.json:historicalEvidenceSha256',
                                         'evidence/nss160-mainline.json:historicalCpuEvidence.historicalEvidenceSha256'],
              'historicalEvidencePath': relative, 'historicalGitRef': base,
              'originalRecordedWorkspaceBytesSha256': sha(working), 'actualGitBlobSha256': sha(actual),
              'reason': 'Working copy CRLF became LF under existing text=auto eol=lf attributes; the original record used workspace bytes',
              'onlyLineEndingsDiffer': True, 'jsonContentExactlyEqual': True,
              'originalMetadataAndFailedCommitRetained': True, 'originalCpuMetricsUnchanged': True,
              'originalExperimentalAndFrozenSourceBytesUnchanged': True,
              'noNewProductionExperiment': True, 'failedPublicationCommit': commit}
for filename, item in [('nss160-publication-archive-failure.json', failure),
                       ('nss160-publication-archive-correction.json', correction)]:
    for dest in [repo / 'evidence' / filename, r / filename]:
        with dest.open('x', encoding='utf-8') as f:
            json.dump(item, f, indent=2); f.write('\n')
print(json.dumps({'passed': True, 'originalMetadataKept': True, 'contentEqual': True, 'gitByteDigestCorrected': True}))
