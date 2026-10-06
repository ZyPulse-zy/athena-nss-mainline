from pathlib import Path
import json
r=Path('work/nss159')
s=(r/'qualify.mjs').read_text(encoding='utf-8')
assert "'qualify.mjs'" in s
s=s.replace("'qualify.mjs'","'qualify.mjs','prepare-qualification-v2.py','qualify-v2.mjs'")
s=s.replace("/\\b(?:from|import)\\s*['\"]", "/(?<!['\"])\\b(?:from|import)\\s*['\"]")
(r/'qualify-v2.mjs').write_text(s,encoding='utf-8',newline='\n')
(r/'qualification-v1-failure.json').write_text(json.dumps({'passed':False,'productionExecuted':False,'reason':'Dependency scanner matched a quoted example from module-stage rather than an import; no source qualification produced','originalQualifierPreserved':'work/nss159/qualify.mjs'},indent=2)+'\n',encoding='utf-8')
print('Saved failed qualifier; scanner ignores directly quoted import examples')
