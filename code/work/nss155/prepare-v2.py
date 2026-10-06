from pathlib import Path
r=Path(__file__).resolve().parent
for a,b in [('pilot-supervisor.mjs','pilot-supervisor-v2.mjs'),('epoch-driver.mjs','epoch-driver-v2.mjs')]:
    p=r/b;assert not p.exists()
    s=(r/a).read_text(encoding='utf-8').replace('run1','run2').replace("from './session-binding.mjs'","from './session-binding-v2.mjs'")
    if a.startswith('pilot'):s=s.replace("from './epoch-driver.mjs'","from './epoch-driver-v2.mjs'").replace("root+'/frozen-qualified-inputs'","root+'/frozen-qualified-inputs-v2'").replace("root+'/frozen-qualified-inputs/'","root+'/frozen-qualified-inputs-v2/'").replace("root+'/entry-source-manifest.json'","root+'/entry-source-manifest-v2.json'")
    p.write_text(s,encoding='utf-8',newline='')
print('Second finite attempt; failed run1 and its exact qualified source inputs remain unchanged. Client/native policy unchanged.')
