from pathlib import Path
r=Path(__file__).resolve().parent
def write(n,s):
    p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
write('epoch-driver-v4.mjs',(r/'epoch-driver-v3.mjs').read_text(encoding='utf-8').replace('./session-binding-v3.mjs','./session-binding-v4.mjs'))
s=(r/'pilot-supervisor-v3.mjs').read_text(encoding='utf-8').replace('./session-binding-v3.mjs','./session-binding-v4.mjs').replace('./epoch-driver-v3.mjs','./epoch-driver-v4.mjs').replace("out=root+'/run3'","out=root+'/run4'").replace('frozen-qualified-inputs-v3','frozen-qualified-inputs-v4').replace('entry-source-manifest-v3.json','entry-source-manifest-v4.json');write('pilot-supervisor-v4.mjs',s)
s=(r/'session-binding-v3.mjs').read_text(encoding='utf-8').replace("from './session-binding-v2.mjs'","from './session-binding-v3.mjs'").replace('entry-qualified-v3.json','entry-qualified-v4.json');write('session-binding-v4.mjs',s)
print('Fresh output namespace only; raw fixture, NSS native and eight-candidate limit unchanged.')
