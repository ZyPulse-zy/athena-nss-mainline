from pathlib import Path
import json
r=Path(__file__).resolve().parent
for name in ['epoch-driver','journal','process-identity','pilot-supervisor','restart-harness']:
    source=r/(name+'-v2.mjs');target=r/(name+'-v3.mjs');assert not target.exists()
    text=source.read_text(encoding='utf-8').replace('run2','run3').replace('entry-source-manifest-v2.json','entry-source-manifest-v3.json').replace('frozen-qualified-inputs-v2','frozen-qualified-inputs-v3')
    for dependency in ['session-binding','epoch-driver','journal','process-identity','pilot-supervisor']:
        text=text.replace(dependency+'-v2.mjs',dependency+'-v3.mjs')
    if name=='epoch-driver':
        assert text.count('work/nss49/session-binding-v3.mjs')==1
        text=text.replace('work/nss49/session-binding-v3.mjs','work/nss49/session-binding.mjs')
    target.write_text(text,encoding='utf-8',newline='')
p=r/'load-v2-reference-private.json';assert not p.exists();p.write_bytes((r/'load-latest-private.json').read_bytes())
print('Incorrect historical dependency is fixed only in v3; all v2 inputs and failure are retained.')
