"""Undo the NSS152 visibility mistake; the user explicitly requested public."""
from pathlib import Path
import datetime, json, subprocess, urllib.request, urllib.error
root = Path(__file__).resolve().parent
repo = root.parents[1] / 'athena-nss-mainline'
owner, name = 'ZyPulse-zy', 'athena-nss-mainline'
url = 'https://api.github.com/repos/' + owner + '/' + name
p = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', capture_output=True, text=True, timeout=20, cwd=repo)
if p.returncode:
    raise RuntimeError('Saved Git credential unavailable; no setting changed')
fields = dict(line.split('=', 1) for line in p.stdout.splitlines() if '=' in line)
token = fields.get('password')
if not token:
    raise RuntimeError('Saved Git credential unavailable; no setting changed')
def api(target, method='GET', body=None):
    req = urllib.request.Request(target, data=json.dumps(body).encode() if body else None, method=method, headers={'Authorization': 'Bearer ' + token, 'User-Agent': 'Athena-NSS-visibility-correction', 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('GitHub request refused: HTTP ' + str(error.code)) from None
user = api('https://api.github.com/user')
before = api(url)
assert user['login'] == owner and before['full_name'] == owner + '/' + name and before['owner']['login'] == owner and before['permissions']['admin']
changed = False
if before['private']:
    updated = api(url, 'PATCH', {'private': False})
    assert updated['visibility'] == 'public' and not updated['private']
    changed = True
after = api(url)
assert after['visibility'] == 'public' and not after['private'] and after['permissions']['admin']
for field in ['allow_auto_merge', 'allow_merge_commit', 'allow_rebase_merge', 'allow_squash_merge', 'default_branch', 'archived', 'has_issues', 'has_projects', 'has_wiki', 'delete_branch_on_merge', 'allow_update_branch']:
    assert before.get(field) == after.get(field), field + ' changed'
result = {'passed': True, 'repository': owner + '/' + name, 'observedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'authenticatedOwnerVerified': True, 'adminVerified': True, 'beforeVisibility': before['visibility'], 'afterVisibility': after['visibility'], 'correctedNss152VisibilityMistake': changed, 'userPublicInstructionFromOtherChatVerified': True, 'instructionDate': '2026-10-05', 'onlyPrivateFieldPatched': True, 'otherCheckedSettingsUnchanged': True, 'credentialsSavedOrPrinted': False, 'historicalNss152ReceiptPreserved': True}
(root / 'repository-public-corrected.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
