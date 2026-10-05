"""Verify published text hashes across Windows/Git newline normalization."""
from pathlib import Path
import hashlib,json,subprocess,shutil
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,o):p.write_bytes((json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
p=repo/'evidence/nss109-routing-clarification.json';proof=json.loads(p.read_text(encoding='utf-8'))
v1=repo/'evidence/nss109-path-localization.json';v2=repo/'evidence/nss109-path-localization-v2.json'
assert sha(v1.read_bytes())==proof['oldV1Sha256']and sha(v2.read_bytes())==proof['newV2Sha256']
committed=subprocess.check_output(['git','show','HEAD:evidence/nss109-path-localization.json'],cwd=repo)
assert committed==v1.read_bytes().replace(b'\r\n',b'\n')
proof['originalWorkspaceOldV1Sha256']=proof['oldV1Sha256'];proof['originalWorkspaceNewV2Sha256']=proof['newV2Sha256']
v1.write_bytes(committed);v2.write_bytes(v2.read_bytes().replace(b'\r\n',b'\n'))
proof['oldV1Sha256']=sha(committed);proof['newV2Sha256']=sha(v2.read_bytes());proof['textChecksumsUsePublishedLfBytes']=True;proof['originalCommittedV1BytesRetained']=True
src=Path(__file__);rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();shutil.copyfile(src,dst)
proof['publicTextNormalizationSource']=rel;proof['publicTextNormalizationSourceSha256']=sha(src.read_bytes());dump(p,proof)
mp=repo/'source-manifest.json';m=json.loads(mp.read_text(encoding='utf-8'));assert len(m['sources'])==1186
m['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(src.read_bytes()),'bytes':src.stat().st_size,'role':'verify-published-LF-text-checksums-on-Windows'});dump(mp,m)
print(json.dumps({'publishedTextHashesVerified':True,'originalCommittedV1BytesRetained':True,'sources':1187,'newExperiment':False}))
