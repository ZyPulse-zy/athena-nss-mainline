from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parent
for name in ['verify-receivers.mjs','verify-downloaders.mjs']:
    p=r/name;body=p.read_bytes();saved=r/name.replace('.mjs','-v1-refused.mjs');assert not saved.exists();saved.write_bytes(body)
    s=body.decode('utf-8');assert 'work/nss154/' in s;s=s.replace('work/nss154/','work/nss155/');p.write_text(s,encoding='utf-8',newline='')
receipt={'failedBeforePublication':True,'error':'EEXIST','cause':'Copied postcheck contained literal output paths to frozen nss154, exclusive-create refused','previousEvidenceOverwritten':False,'nativeExperimentSourcesChanged':False,'originalBadPostcheckSourcesPreserved':True,'fixedScope':'Only two postcheck output path namespaces nss154 to nss155'}
(r/'postcheck-path-failure.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
