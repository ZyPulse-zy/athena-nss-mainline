"""Keep the five-flow NSS/QoS entry; serialize only own fixture SSH handshakes."""
from pathlib import Path
import shutil

w = Path(__file__).resolve().parents[1]
old = w / 'work/v23-fiveflow'; r = w / 'work/v24-fiveflow'; r.mkdir()
for p in old.iterdir():
    if not p.is_file() or p.suffix not in ['.mjs', '.lua', '.py', '.ps1'] or any(x in p.name for x in ['failed', 'qualify', 'repair', 'analyze', 'inspect-ssh']):
        continue
    data = p.read_bytes().replace(b'work/v23-fiveflow', b'work/v24-fiveflow').replace(rb'work\/v23-fiveflow\/', rb'work\/v24-fiveflow\/')
    data = data.replace(b'v23-fiveflow-', b'v24-fiveflow-')
    if p.name == 'session-binding.mjs':
        data = data.replace(b'../v22-fiveflow/session-binding.mjs', b'../v23-fiveflow/session-binding.mjs')
    if p.name == 'pilot-supervisor.mjs':
        data = data.replace(b'entry:\'v23 five', b'entry:\'v24 five')
        data = data.replace(b"await run(root+'/match-controlled.mjs');", b"await run(root+'/wait-four-ssh.mjs',[],35);\r\n await run(root+'/match-controlled.mjs');")
    (r / p.name).write_bytes(data)
for name in ['native-qualified.json', 'normalizer-qualified.json', 'qos-native-qualified.json']:
    shutil.copy2(old / name, r / name)
p = r / 'native-client.mjs'; data = p.read_bytes()
needle = b"children.set(slot,p);s.ownerPid=p.pid;s.executable=sshExe;s.spawnedAt=new Date().toISOString();let stderr='';"
replacement = needle + b"let readyDone=false,acceptFirst,rejectFirst;const first=new Promise((resolve,reject)=>{acceptFirst=resolve;rejectFirst=reject});const readyTimer=setTimeout(()=>{if(!readyDone){readyDone=true;rejectFirst(Error('Owned SSH first-byte deadline '+slot))}},8000);const failedFirst=e=>{if(!readyDone){readyDone=true;clearTimeout(readyTimer);rejectFirst(e)}};"
assert data.count(needle) == 1; data = data.replace(needle, replacement)
needle = b's.connected=true;s.bytes+=b.length;'
replacement = b"s.connected=true;if(!readyDone){readyDone=true;clearTimeout(readyTimer);acceptFirst()}s.bytes+=b.length;"
assert data.count(needle) == 1; data = data.replace(needle, replacement)
data = data.replace(b"p.on('error',e=>{if(p===children.get(slot))finish(e);});", b"p.on('error',e=>{failedFirst(e);if(p===children.get(slot))finish(e);});")
data = data.replace(b"p.on('close',code=>{if(p===children.get(slot)", b"p.on('close',code=>{failedFirst(Error('Owned SSH closed before first byte '+slot));if(p===children.get(slot)")
needle = b'rotating.delete(slot);stamp();'
assert data.count(needle) == 1; data = data.replace(needle, b'rotating.delete(slot);stamp();try{await first}finally{clearTimeout(readyTimer)};')
needle = b"for(const slot of ['tcp','tcp2','tcp3','tcp4'])await startTcp(slot,1);"
assert data.count(needle) == 1; data = data.replace(needle, b"try{for(const slot of ['tcp','tcp2','tcp3','tcp4'])await startTcp(slot,1)}catch(error){finish(error)};")
p.write_bytes(data)
print('v24 fixture first-byte handshake serialized with 8-second bound; old global client/NSS/QoS limits retained')
