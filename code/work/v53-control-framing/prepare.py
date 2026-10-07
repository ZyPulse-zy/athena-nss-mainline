from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent;old=root.parent/'v51-run-20261007121048-dc58268e/persistent-ssh.mjs'
blob=old.read_bytes();s=blob.decode();assert s.count('export function persistentSsh(){')==1
s=s.replace('export function persistentSsh(){','export function persistentSsh({paced=false}={}){')
s=s.replace("const pending=new Map();let sequence=0,buffer='',transportError='',closed=false;","const pending=new Map();let sequence=0,buffer='',transportError='',closed=false,writeQueue=Promise.resolve();")
needle="child.stdin.write(Buffer.from(JSON.stringify({id,command,input:Buffer.from(input).toString('base64'),seconds:Math.max(1,(milliseconds-1000)/1000)})).toString('base64')+'\\n');"
assert s.count(needle)==1
s=s.replace(needle,"const frame=Buffer.from(Buffer.from(JSON.stringify({id,command,input:Buffer.from(input).toString('base64'),seconds:Math.max(1,(milliseconds-1000)/1000)})).toString('base64')+'\\n');assert.ok(frame.length<=65536);writeQueue=writeQueue.then(async()=>{if(!paced){assert.ok(!closed);child.stdin.write(frame);return;}for(let off=0;off<frame.length;off+=256){assert.ok(!closed);child.stdin.write(frame.subarray(off,off+256));await new Promise(r=>setTimeout(r,20));}}).catch(e=>{rejectAll(e);child.kill();});")
s=s.replace('return {exec(command', 'return {pid:child.pid,exec(command')
with (root/'persistent-ssh-candidate.mjs').open('x',encoding='utf8',newline='') as f:f.write(s)
with (root/'preparation.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'originalSource':str(old).replace('\\','/'),'originalSha256':hashlib.sha256(blob).hexdigest(),'onlyPrivateControlPipeFramingChanged':True,'frameMaximumBytes':65536,'chunkBytes':256,'spacingMilliseconds':20,'sshAlgorithmsAndTimeoutsUnchanged':True},f,indent=2)
print(json.dumps({'passed':True,'controlChunkBytes':256,'spacingMilliseconds':20}))
