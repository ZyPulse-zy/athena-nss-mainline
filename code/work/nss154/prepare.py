"""New journalled supervisor; old native factory and all network budgets unchanged."""
from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'nss153'
names=['start-dallas.mjs','match-controlled.mjs','read-controlled.mjs','current-audit-diagnostic.mjs','failed-wan-owner.lua','declared-baseline.mjs','ssh-client.mjs','bounded-pacer.mjs','upload-ack.mjs','upload-server.py','server.py','discover-peer.py','probe-peer.py','client-watchdog.ps1','endpoint-firewall-guardian.py','close-endpoint.mjs','crash-read.lua']
assert all((old/n).is_file() for n in names)
def put(n,s):
    p=r/n;assert not p.exists(),n;p.write_text(s,encoding='utf-8',newline='')
def namespace(s):return s.replace('work/nss153','work/nss154').replace('work\\/nss153','work\\/nss154').replace('nss153-','nss154-').replace('NSS153','NSS154')
for n in names:put(n,namespace((old/n).read_text(encoding='utf-8')))
s=namespace((old/'epoch-session.mjs').read_text(encoding='utf-8'))
old_entry="const mode=process.argv[2]??'inspect';assert.ok(['inspect','epoch'].includes(mode));"
assert s.count(old_entry)==1
s=s.replace(old_entry,"export async function runEpoch(continuityPath,onDetached){\nconst mode='epoch';assert.equal(typeof onDetached,'function');")
s=s.replace("  const continuityPath=process.argv[3];assert.equal(continuityPath,'work/nss154/run1/continuity-private.json');", "  assert.equal(continuityPath,'work/nss154/run1/continuity-private.json');")
assert s.count('await uploadStage(context);let latest;')==1
s=s.replace('await uploadStage(context);let latest;', 'await onDetached(context);await uploadStage(context);let latest;')
s=s.replace("console.log(JSON.stringify({passed:failures.length===0,mode:'epoch',output:dir,errors:failures}));", "return {passed:completed&&failures.length===0,mode:'epoch',output:dir,errors:failures};")
s+='\n}\n'
put('epoch-driver.mjs',s)
print('Journal callback inserted after independent checkpoint/guardian qualification and before upload; original native factory149 unchanged.')
