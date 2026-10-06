"""Fix only the export directory predicate; original failure stays byte-identical."""
from pathlib import Path
import json
p=Path(__file__).resolve().with_name('export-failure.py');s=p.read_text(encoding='utf8')
needle="loads=sorted(r.glob('load-*'));assert len(loads)==1;load=loads[0]"
assert s.count(needle)==1
marker=p.with_name('failed-export-directory-predicate.json')
with marker.open('x',encoding='utf8')as f:json.dump({'failed':True,'originalSource':'export-failure.py','directoryPatternAlsoMatchedLoadLatestFile':True,'failureBeforeRepositoryWrites':True,'commitChainStopped':True,'productionWrites':False},f,indent=2)
s=s.replace(needle,"loads=sorted(p for p in r.glob('load-*') if p.is_dir());assert len(loads)==1;load=loads[0]")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
