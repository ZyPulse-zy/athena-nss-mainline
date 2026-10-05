import json,re,difflib
from pathlib import Path
a=json.loads(Path('work/nss68/nss107-final-20261005-baseline-private.json').read_text());b=json.loads(Path('work/nss109/final-baseline-private.json').read_text())
for k in ['rules','pbr','nftRuleset']:
 aa=a[k].splitlines();bb=b[k].splitlines();diff=list(difflib.unified_diff(aa,bb,n=1));print('FIELD '+k)
 for l in diff[:130]:
  l=re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b','[IP]',l);l=re.sub(r'\b[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}\b','[MAC]',l);print(l)
