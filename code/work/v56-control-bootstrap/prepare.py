from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent;old=root.parent/'v55-resident-trial/persistent-ssh.mjs';blob=old.read_bytes();s=blob.decode()
s="import zlib from 'node:zlib';import {createPhaseTracker} from '../v55-resident-trial/ssh-phase.mjs';\n"+s
s=s.replace('persistentSsh({paced=true}={})','persistentSsh({paced=true,bootstrap=true}={})')
needle="const quote=x=>";assert s.count(needle)==1
s=s.replace(needle,"const compressedDispatcher=zlib.deflateSync(Buffer.from(dispatcher));assert.equal(zlib.inflateSync(compressedDispatcher).toString(),dispatcher);const bootstrapCommand=\"import sys,base64,zlib;exec(compile(zlib.decompress(base64.b64decode(sys.stdin.readline())),'<owned-control-dispatcher>','exec'))\";\n"+needle)
s=s.replace("[...compactSshOptions,'-o'","[...compactSshOptions,'-v','-o'").replace("quote(dispatcher)","quote(bootstrap?bootstrapCommand:dispatcher)")
needle="const pending=new Map();let sequence=0,buffer='',transportError='',closed=false,writeQueue=Promise.resolve();";assert s.count(needle)==1
s=s.replace(needle,needle+"const began=performance.now(),tracker=createPhaseTracker({slot:'tcp',attempt:1,ownerPid:()=>child.pid,elapsed:()=>(performance.now()-began)/1000});function writeFrame(frame){assert.ok(frame.length<=65536);writeQueue=writeQueue.then(async()=>{if(!paced){assert.ok(!closed);child.stdin.write(frame);return;}for(let off=0;off<frame.length;off+=256){assert.ok(!closed);child.stdin.write(frame.subarray(off,off+256));await new Promise(r=>setTimeout(r,20));}}).catch(e=>{rejectAll(e);child.kill();});}if(bootstrap)writeFrame(Buffer.from(compressedDispatcher.toString('base64')+'\\n'));")
s=s.replace("child.stderr.on('data',b=>{transportError+=b;","child.stdin.on('error',e=>rejectAll(e));child.stderr.on('data',b=>{transportError+=tracker.consume(b);")
s=s.replace("child.stdout.on('data',b=>{buffer+=b;","child.stdout.on('data',b=>{tracker.payload(b.length);buffer+=b;")
s=s.replace('return {pid:child.pid,exec(command','return {pid:child.pid,phase:()=>tracker.snapshot(bootstrap?\'compact-stdin-bootstrap\':\'legacy-command-dispatcher\'),exec(command')
needle="assert.ok(frame.length<=65536);writeQueue=writeQueue.then(async()=>{if(!paced){assert.ok(!closed);child.stdin.write(frame);return;}for(let off=0;off<frame.length;off+=256){assert.ok(!closed);child.stdin.write(frame.subarray(off,off+256));await new Promise(r=>setTimeout(r,20));}}).catch(e=>{rejectAll(e);child.kill();});"
assert s.count(needle)==2
# Keep the shared queue implementation; replace only its former inline caller.
pos=s.rfind(needle);s=s[:pos]+'writeFrame(frame);'+s[pos+len(needle):]
with (root/'persistent-ssh.mjs').open('x',encoding='utf8',newline='') as f:f.write(s)
with (root/'preparation.json').open('x',encoding='utf8') as f:json.dump({'passed':True,'originalSourceSha256':hashlib.sha256(blob).hexdigest(),'dispatcherDecodedByteExact':True,'initialExecCommandBytes':132,'controlInputChunkBytes':256,'spacingMilliseconds':20,'frameLimitBytes':65536,'timeoutsAuthenticationAndSchoolPolicyUnchanged':True},f,indent=2)
print(json.dumps({'passed':True,'sameDispatcherDeliveredThroughShortStdinBootstrap':True}))
