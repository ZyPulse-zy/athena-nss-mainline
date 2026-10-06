"""Preserve frozen source bytes after the exact staged blank-at-EOF refusal."""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parents[2];repo=w/'athena-nss-mainline';read=lambda p:json.loads(p.read_text(encoding='utf-8'));dump=lambda v:json.dumps(v,ensure_ascii=False,indent=2)+'\n';sha=lambda b:hashlib.sha256(b).hexdigest()
name='code/work/nss159/endpoint-firewall-guardian.py';source=w/'work/nss159/endpoint-firewall-guardian.py';assert source.read_bytes()==(repo/name).read_bytes()
repair={'passed':True,'initialStagedDiffCheckPassed':False,'initialFailure':'code/work/nss159/endpoint-firewall-guardian.py:119: new blank line at EOF.','commitChainStoppedBeforeCommit':True,'frozenSourceBytesUnchanged':True,'sourcePath':name,'sourceSha256':sha(source.read_bytes()),'pathSpecificWhitespaceAttribute':'whitespace=cr-at-eol,-blank-at-eof','noGlobalWhitespaceRelaxation':True}
p=repo/'.gitattributes';s=p.read_text(encoding='utf-8');assert '/'+name+' whitespace=' not in s;s+='\n# Preserve exact qualified NSS159 inherited guardian and historical runtime bytes.\n/'+name+' whitespace=cr-at-eol,-blank-at-eof\n/evidence/nss158-runtime.json -text\n';p.write_text(s,encoding='utf-8')
p=repo/'evidence/nss159-publication-whitespace-repair.json';assert not p.exists();p.write_text(dump(repair),encoding='utf-8')
self=Path(__file__).resolve();relative=self.relative_to(w).as_posix();b=self.read_bytes();target=repo/'code'/relative;assert not target.exists();target.write_bytes(b)
p=repo/'source-manifest.json';m=read(p);assert len(m['sources'])==2752;m['sources'].append({'path':'code/'+relative,'workspaceSource':relative,'sha256':sha(b),'bytes':len(b),'role':'exact-path-whitespace-repair-preserve-frozen-source'});p.write_text(dump(m),encoding='utf-8')
p=repo/'evidence/nss159-source-proof.json';proof=read(p);assert proof['sources']==65;proof['sourceHashes'][relative]=sha(b);proof['sources']=66;p.write_text(dump(proof),encoding='utf-8')
p=repo/'evidence/nss159-mainline.json';main=read(p);assert main['sourcesAdded']==65;main['sourcesAdded']=66;main['publicationWhitespaceRepair']=repair;p.write_text(dump(main),encoding='utf-8')
p=repo/'tools/check_repository.py';s=p.read_text(encoding='utf-8');anchor="print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))";assert s.count(anchor)==1
check="publication159=load159('publication-whitespace-repair');assert publication159==x159['publicationWhitespaceRepair'] and publication159['passed'] and not publication159['initialStagedDiffCheckPassed'] and publication159['commitChainStoppedBeforeCommit'] and publication159['frozenSourceBytesUnchanged'] and publication159['noGlobalWhitespaceRelaxation']\nassert publication159['sourceSha256']==hashlib.sha256((root/publication159['sourcePath']).read_bytes()).hexdigest()\n"
p.write_text(s.replace(anchor,check+anchor),encoding='utf-8')
print(json.dumps(repair))
