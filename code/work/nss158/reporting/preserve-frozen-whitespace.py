"""Retain the first failed check and exact bytes; only four path attributes."""
from pathlib import Path
import json,hashlib
w=Path(__file__).resolve().parents[3];r=w/'athena-nss-mainline';p=w/'work/nss158/reporting'
read=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
x=read(p/'publication-whitespace-failure.json');assert x['exitCode']==1 and x['commitAndPushStopped'] and not x['frozenSourceBytesChanged']
proof=read(r/'evidence/nss158-source-proof.json')
paths=['code/work/nss157/endpoint-firewall-guardian.py','code/work/nss157/fast-path-v2.lua','code/work/nss157/fast-path.lua','code/work/nss158/fast-path.lua']
for f in paths:assert hashlib.sha256((r/f).read_bytes()).hexdigest()==proof['sourceHashes'][f.removeprefix('code/')]
attrs=r/'.gitattributes';s=attrs.read_text(encoding='utf-8')
s+='\n# Preserve the four exact frozen NSS157/158 sources after failed staged check.\n'
for f in paths:s+='/'+f+' whitespace=cr-at-eol,-'+('blank-at-eof' if f.endswith('.py') else 'blank-at-eol')+'\n'
attrs.write_text(s,encoding='utf-8')
f='work/nss158/reporting/preserve-frozen-whitespace.py';b=(w/f).read_bytes();h=hashlib.sha256(b).hexdigest();dest=r/'code'/f;assert not dest.exists();dest.write_bytes(b)
m=read(r/'source-manifest.json');assert m['lastAppendExport']=='NSS158';m['sources'].append({'path':'code/'+f,'workspaceSource':f,'sha256':h,'bytes':len(b),'role':'publication-failed-check-preservation-only-exact-four-path-attributes'})
(r/'source-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ev=r/'evidence/nss158-publication-whitespace-check.json';assert not ev.exists()
ev.write_text(json.dumps({**x,'exactPathAttributes':paths,'sourceHashesStillMatch':True,'repairSource':f,'repairSourceSha256':h},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='\n首次暂存whitespace检查在提交前拒绝，提交/推送链已停止；保留原失败，只给四个固定冻结源码加路径专属blank-at-eof/blank-at-eol属性，原源码SHA不变。见 [格式检查证据](LINK)。\n'
for name in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
 dest=r/name;body=dest.read_text(encoding='utf-8');anchor='\n## NSS156及更早历史\n';assert anchor in body;link=('../' if name.startswith('docs/') else '')+'evidence/nss158-publication-whitespace-check.json';body=body.replace(anchor,text.replace('LINK',link)+anchor,1);dest.write_text(body,encoding='utf-8')
checker=r/'tools/check_repository.py';s=checker.read_text(encoding='utf-8');anchor="assert manifest['lastAppendExport']=='NSS158'";assert s.count(anchor)==1
new="\nwp158=load158('publication-whitespace-check');assert wp158['exitCode']==1 and wp158['commitAndPushStopped'] and not wp158['frozenSourceBytesChanged'] and wp158['sourceHashesStillMatch'] and len(wp158['exactPathAttributes'])==4\nassert hashlib.sha256((root/'code'/wp158['repairSource']).read_bytes()).hexdigest()==wp158['repairSourceSha256']\n"
checker.write_text(s.replace(anchor,new+anchor),encoding='utf-8')
print(json.dumps({'preservedFirstFailure':True,'originalSourcesUnchanged':True,'onlyFourExactPathAttributes':True,'sourcesTotal':len(m['sources'])}))
