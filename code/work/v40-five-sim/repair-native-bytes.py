from pathlib import Path
import ast,json,hashlib
r=Path('work/v40-five-sim');d=r/'qualification-first-failure';d.mkdir()
for name in ['qualify-entry.mjs','native-client.mjs']:
 with (d/name).open('xb') as f:f.write((r/name).read_bytes())
values={}
for node in ast.parse((r/'prepare.py').read_text()).body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['a','b']:values[node.targets[0].id]=ast.literal_eval(node.value)
data=Path('work/v39-five-sim/native-client.mjs').read_bytes();a=values['a'].encode();b=values['b'].encode();assert data.count(a)==1
fixed=data.replace(a,b).replace(b'work/v39-five-sim',b'work/v40-five-sim').replace(b'work\\/v39-five-sim\\/',b'work\\/v40-five-sim\\/').replace(b'v39-five-sim-',b'v40-five-sim-')
with (d/'failure.json').open('x',encoding='utf8') as f:json.dump({'exitCode':1,'reason':'Mixed newline bytes were normalized in fixture preparation, then all lines were incorrectly changed to CRLF','networkOrNssStarted':False,'repairedByExactOriginalBytesAndOnlyDeclaredControlReplacement':True,'failedNativeSha256':hashlib.sha256((r/'native-client.mjs').read_bytes()).hexdigest(),'fixedNativeSha256':hashlib.sha256(fixed).hexdigest()},f,indent=2);f.write('\n')
(r/'native-client.mjs').write_bytes(fixed)
print(json.dumps({'passed':True,'exactOriginalNewlineBytesPreserved':True,'priorQualificationFailureSaved':True,'productionNotStarted':True}))
