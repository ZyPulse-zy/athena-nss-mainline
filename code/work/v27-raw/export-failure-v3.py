"""Resume only verified partial source copies and include pure qualification JSON."""
from pathlib import Path
import json
p=Path(__file__).resolve().with_name('export-failure.py');s=p.read_text(encoding='utf8')
replacements={
 "loads=sorted(r.glob('load-*'));assert len(loads)==1;load=loads[0]":"loads=sorted(p for p in r.glob('load-*') if p.is_dir());assert len(loads)==1;load=loads[0]",
 "assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base and not subprocess.check_output(['git','status','--porcelain'],cwd=repo)":"assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==base\nassert set(subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).splitlines())=={'?? code/work/prepare-v27-raw.py','?? code/work/v27-raw/'}",
 "p.suffix not in ['.mjs','.lua','.py','.ps1','.md']":"(p.suffix not in ['.mjs','.lua','.py','.ps1','.md'] and p.name not in ['native-qualified.json','normalizer-qualified.json','qos-native-qualified.json','raw-model-qualified.json'])",
 "with dst.open('xb')as out:out.write(b)":"if dst.exists():assert dst.read_bytes()==b,f\n    else:\n        with dst.open('xb')as out:out.write(b)",
 "m=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3801;hashes={}":"data['retainedPublicationFailures']=[{'error':'directory glob matched the load-latest JSON file','beforeRepositoryWrites':True},{'error':'qualification JSON missing from the curated source copy','partialSourceCopiesVerifiedBeforeResume':True}]\nm=read(repo/'source-manifest.json');prefix=copy.deepcopy(m['sources']);assert len(prefix)==3801;hashes={}"
}
for old,new in replacements.items():assert s.count(old)==1,old;s=s.replace(old,new)
with p.with_name('failed-export-qualification-json.json').open('x',encoding='utf8')as f:json.dump({'failed':True,'priorSource':'export-failure-v2.py','pureQualificationJsonWasNotInCopyAllowlist':True,'stoppedBeforeEvidenceManifestAndCommitWrites':True,'partialCopiesMustMatchWorkspaceBytesToResume':True,'productionWrites':False},f,indent=2)
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
