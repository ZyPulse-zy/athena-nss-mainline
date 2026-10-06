"""Preserve failed publication history and frozen source bytes; no force-push."""
from pathlib import Path
import json,hashlib,subprocess
w=Path(__file__).resolve().parents[3];repo=w/'athena-nss-mainline';r=w/'work/nss155';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda b:hashlib.sha256(b).hexdigest()
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();assert commit.startswith('627f8c4')
file='code/work/nss155/fast-path.lua';assert subprocess.check_output(['git','show',commit+':'+file],cwd=repo)==(w/'work/nss155/fast-path.lua').read_bytes()
failure={'case':'publication-staged-whitespace','check':'git diff --cached --check','exitCode':1,'file':file,'line':191,'cause':'Inherited whitespace-only line in frozen fast-path source','failedCommitPreserved':commit,'commitAndPushIncorrectlyContinuedAfterFailedCheck':True,'workflowErrorAcknowledged':True,'frozenSourceEdited':False,'forcePushOrHistoryRewrite':False,'correction':'Path-specific blank-at-eol attribute; subsequent publication uses explicit exit-code gates'}
(r/'reporting/publication-whitespace-failure.json').write_text(json.dumps(failure,indent=2)+'\n',encoding='utf-8')
p=repo/'evidence/nss155-failures.json';f=read(p);assert len(f)==4;f.append(failure);p.write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
attrs=repo/'.gitattributes';s=attrs.read_text();s+='\n# Preserve the exact qualified fast-path whitespace; scope this exception only.\n/code/work/nss155/fast-path.lua whitespace=cr-at-eol,-blank-at-eol\n';attrs.write_text(s,encoding='utf-8')
p=repo/'source-manifest.json';manifest=read(p);assert len(manifest['sources'])==2429
source='work/nss155/reporting/repair-publication-whitespace.py';b=(w/source).read_bytes();dest=repo/'code'/source;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);manifest['sources'].append({'path':'code/'+source,'workspaceSource':source,'sha256':sha(b),'bytes':len(b),'role':'explicit-publication-failure-correction'});p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=repo/'evidence/nss155-source-proof.json';proof=read(p);assert proof['sources']==58;proof['sources']=59;proof['sourceHashes'][source]=sha(b);p.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=repo/'evidence/nss155-mainline.json';main=read(p);main.update(failuresPreserved=5,exportedSources=59,publicationWhitespaceFailureCommitPreserved=commit);p.write_text(json.dumps(main,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=repo/'tools/check_repository.py';s=p.read_text();assert s.count("assert len(f155)==4 and x155['failuresPreserved']==4")==1;s=s.replace("assert len(f155)==4 and x155['failuresPreserved']==4","assert len(f155)==5 and x155['failuresPreserved']==5\nassert f155[4]['commitAndPushIncorrectlyContinuedAfterFailedCheck'] and f155[4]['workflowErrorAcknowledged'] and not f155[4]['frozenSourceEdited'] and not f155[4]['forcePushOrHistoryRewrite']");p.write_text(s,encoding='utf-8')
note='发布流程更正：首次暂存whitespace检查拒绝后编排仍提交并推送627f8c4，是本轮流程错误。该提交、原错误和冻结源码保留；只增加该源码路径的blank-at-eol属性例外。后续检查逐步核验退出码后才允许提交/推送，实际archive结果另存收据。'
for n in ['AGENTS.md','docs/STATE.md','docs/PLAN.md','docs/EXPERIMENT_LOG.md']:
    p=repo/n;s=p.read_text(encoding='utf-8');s=s.replace('## NSS154及更早历史',note+'\n\n## NSS154及更早历史',1);p.write_text(s,encoding='utf-8')
for p in [repo/'reports/nss155-mainline-report.html',w/'outputs/nss155-mainline-report.html']:
    s=p.read_text(encoding='utf-8');s=s.replace('</pre>','\n'+note+'</pre>',1);p.write_text(s,encoding='utf-8')
print(json.dumps({'failurePreserved':True,'failedCommit':commit,'frozenSourceByteExact':True,'newSourceHashesTotal':len(manifest['sources']),'publicationNotYetRevalidated':True}))
