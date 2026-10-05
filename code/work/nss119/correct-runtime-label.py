"""Correct only the historical runtime label; preserve the original export."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';r=w/'work/nss119'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=repo/'evidence/current-runtime.json';raw=p.read_bytes();x=json.loads(raw);assert x['round']=='NSS119'and'historical118RuntimePreservedSha256'not in x
digest=x.pop('historical117RuntimePreservedSha256');assert digest==sha((repo/'evidence/nss118-runtime.json').read_bytes());x['historical118RuntimePreservedSha256']=digest
archive=repo/'evidence/nss119-v1-runtime.json';assert not archive.exists();archive.write_bytes(raw);dump(p,x)
manifest=json.loads((repo/'source-manifest.json').read_text());assert len(manifest['sources'])==1399;prefix=sha(json.dumps(manifest['sources'],sort_keys=True,separators=(',',':')).encode())
src=Path(__file__);rel=src.relative_to(w).as_posix();dst=repo/'code'/rel;assert not dst.exists();shutil.copyfile(src,dst);manifest['sources'].append({'path':'code/'+rel,'workspaceSource':rel,'sha256':sha(src.read_bytes()),'bytes':src.stat().st_size,'role':'runtime-historical-label-correction-only'});manifest['generatedAt']=datetime.now(timezone.utc).isoformat();dump(repo/'source-manifest.json',manifest)
proof={'passed':True,'originalExportV1PreservedSha256':sha(raw),'changedFieldOnly':['historical117RuntimePreservedSha256','historical118RuntimePreservedSha256'],'correctArchivedRuntime':'evidence/nss118-runtime.json','archivedRuntimeSha256':digest,'actualMeasurementsChanged':False,'originalSourceExportUntouched':True,'originalFailedCheckerRetained':True,'historicPrefixSources':1399,'historicPrefixCanonicalSha256':prefix,'newSource':rel,'newSourceSha256':sha(src.read_bytes())};dump(repo/'evidence/nss119-runtime-label-correction.json',proof);dump(r/'runtime-label-correction-receipt.json',proof);print(json.dumps({'passed':True,'metadataLabelOnly':True,'sources':len(manifest['sources'])}))
