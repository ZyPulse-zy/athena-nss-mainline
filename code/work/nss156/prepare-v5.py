from pathlib import Path
r=Path(__file__).resolve().parent
def write(n,s):
    p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'epoch-driver-v4.mjs').read_text(encoding='utf-8').replace('./session-binding-v4.mjs','./session-binding-v5.mjs').replace('work/nss156/run1/','work/nss156/run5/');write('epoch-driver-v5.mjs',s)
s=(r/'pilot-supervisor-v4.mjs').read_text(encoding='utf-8').replace('./session-binding-v4.mjs','./session-binding-v5.mjs').replace('./epoch-driver-v4.mjs','./epoch-driver-v5.mjs').replace("out=root+'/run4'","out=root+'/run5'").replace('frozen-qualified-inputs-v4','frozen-qualified-inputs-v5').replace('entry-source-manifest-v4.json','entry-source-manifest-v5.json');write('pilot-supervisor-v5.mjs',s)
s=(r/'session-binding-v4.mjs').read_text(encoding='utf-8').replace("from './session-binding-v3.mjs'","from './session-binding-v4.mjs'").replace('entry-qualified-v4.json','entry-qualified-v5.json');write('session-binding-v5.mjs',s)
print('Driver exact continuity allowlist matches new harness namespace; earlier frozen versions retained.')
