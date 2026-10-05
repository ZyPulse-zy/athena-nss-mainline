import json,re,difflib
from pathlib import Path
a=json.loads(Path('work/nss68/nss107-final-20261005-baseline-private.json').read_text());b=json.loads(Path('work/nss109/final-baseline-private.json').read_text())
for k in ['pbr','nftRuleset']:
 diff=list(difflib.unified_diff(a[k].splitlines(),b[k].splitlines(),n=1));out=[]
 for l in diff:
  if not l.startswith(('+','-')) or l.startswith(('+++','---')) or 'jump mark_w' in l:continue
  l=re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b','[IP]',l);out.append(l)
 print(json.dumps({'field':k,'nonBucketChangedLines':out},ensure_ascii=True))
