from pathlib import Path
r=Path(__file__).resolve().parent
def write(n,s):
    p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'start-dallas-v2.mjs').read_text(encoding='utf-8')
s=s.replace('const seededUdpPort=priorConfig.udpSourcePort;', 'const seededUdpPort=59000+crypto.randomInt(800);')
s=s.replace('udpNotRotatedDuringMatching:true','udpNotRotatedDuringMatching:true,oneFreshInitialOwnedUdpPort:true,historicalSourcePortNotReused:seededUdpPort!==priorConfig.udpSourcePort')
assert 'const seededUdpPort=59000+crypto.randomInt(800)' in s;write('start-dallas-v3.mjs',s)
write('epoch-driver-v3.mjs',(r/'epoch-driver-v2.mjs').read_text(encoding='utf-8').replace('./session-binding-v2.mjs','./session-binding-v3.mjs'))
s=(r/'pilot-supervisor-v2.mjs').read_text(encoding='utf-8').replace('./session-binding-v2.mjs','./session-binding-v3.mjs').replace('./epoch-driver-v2.mjs','./epoch-driver-v3.mjs').replace("out=root+'/run2'","out=root+'/run3'").replace("root+'/start-dallas-v2.mjs'","root+'/start-dallas-v3.mjs'").replace('frozen-qualified-inputs-v2','frozen-qualified-inputs-v3').replace('entry-source-manifest-v2.json','entry-source-manifest-v3.json')
write('pilot-supervisor-v3.mjs',s)
s=(r/'session-binding-v2.mjs').read_text(encoding='utf-8').replace("from './session-binding.mjs'","from './session-binding-v2.mjs'").replace('entry-qualified-v2.json','entry-qualified-v3.json');write('session-binding-v3.mjs',s)
print('One new UDP source port at startup only; no within-load UDP rotation or router policy change.')
