"""Preserve the pre-read codec error, then run the corrected sanitizer."""
from pathlib import Path
import json

r=Path(__file__).resolve().parent
with (r/'failed-sanitizer-codec.json').open('x',encoding='utf8') as f:
    json.dump({'passed':False,'error':'Python codec spelling utf8-sig unsupported; failed before reading any input',
               'originalSourceRetained':True,'repositoryWritten':False},f,indent=2);f.write('\n')
s=(r/'summarize-progress.py').read_text(encoding='utf8').replace("encoding='utf8-sig'","encoding='utf-8-sig'")
exec(compile(s,str(r/'summarize-progress.py'),'exec'),{'__file__':str(r/'summarize-progress.py'),'__name__':'__main__'})
