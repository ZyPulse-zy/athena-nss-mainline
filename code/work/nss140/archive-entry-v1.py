"""Keep the first offline binding rejection and its exact sources."""
from pathlib import Path
import json,hashlib,shutil
w=Path(__file__).resolve().parents[2];r=w/'work/nss140';p=json.loads((r/'entry-qualified.json').read_bytes())
dst=r/'entry-v1-source-private';dst.mkdir()
for f,h in p['sourceManifest'].items():
 b=(w/f).read_bytes();assert hashlib.sha256(b).hexdigest()==h
 target=dst/f;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
shutil.copyfile(r/'entry-qualified.json',r/'entry-qualified-v1.json')
shutil.copyfile(r/'session-binding.mjs',r/'session-binding-v1.mjs')
(r/'default-inspect-v1-rejection.json').write_text(json.dumps({'passed':False,'stage':'verifyPreparation-before-PC-reader-and-router-connection','observedAtUtc':'2026-10-05T23:11:09Z','error':'AssertionError: pack-guardian.mjs byte equality','actualSha256':'746a9c866d1e80f9494cead571af2f0e44bddacafbd0a55f7df8f75c96378927','expectedSha256':'bb6d49d95ab67cac54aa91b49c79491f573ae57ac34ecf7c019895f5b05c8dd9','cause':'Only temporary placeholder namespace changed NSS138_LITERAL to NSS140_LITERAL; expanded guardian was not changed. Source equality assertion was too broad.','routerConnectionStarted':False,'checkpointOrStageStarted':False,'ecmOpened':False,'firstQualificationSourcesFrozen':len(p['sourceManifest'])},indent=2)+'\n',encoding='utf-8')
(r/'entry-qualified.json').unlink()
print(json.dumps({'frozenSources':len(p['sourceManifest']),'firstEntryQualificationPreserved':True,'productionWrites':False}))
