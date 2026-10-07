import{compactSshOptions}from'../v52-udp-preflight/ssh-options.mjs';
import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';
const dispatcher=`import sys,json,base64,subprocess,threading
lock=threading.Lock()
def emit(v):
 with lock:print(json.dumps(v),flush=True)
def worker(q):
 p=None
 try:
  p=subprocess.Popen(q['command'],shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  def pump(stream,key):
   for b in iter(stream.readline,b''):emit({'id':q['id'],key:base64.b64encode(b).decode()})
  a=threading.Thread(target=pump,args=(p.stdout,'stdout'));b=threading.Thread(target=pump,args=(p.stderr,'stderr'));a.start();b.start()
  p.stdin.write(base64.b64decode(q['input']));p.stdin.close()
  code=p.wait(timeout=q['seconds']);a.join();b.join();emit({'id':q['id'],'code':code})
 except Exception as e:
  if p and p.poll() is None:p.kill()
  emit({'id':q['id'],'error':str(e)})
for line in sys.stdin:
 q=json.loads(base64.b64decode(line));threading.Thread(target=worker,args=(q,)).start()
`;
const quote=x=>"'"+x.replaceAll("'","'\\''")+"'";
export function persistentSsh(){
 const child=spawn('ssh',[...compactSshOptions,'-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=3','-o','ServerAliveCountMax=1','sub2api-dallas','python3 -B -E -s -u -c '+quote(dispatcher)],{windowsHide:true,stdio:['pipe','pipe','pipe']});
 const pending=new Map();let sequence=0,buffer='',transportError='',closed=false;
 function rejectAll(error){for(const p of pending.values()){clearTimeout(p.timer);p.reject(error);}pending.clear();}
 child.stderr.on('data',b=>{transportError+=b;if(transportError.length>16384)child.kill();});
 child.on('error',e=>rejectAll(e));child.on('close',code=>{closed=true;rejectAll(new Error('Owned SSH transport closed '+code+': '+transportError));});
 child.stdout.on('data',b=>{buffer+=b;assert.ok(buffer.length<2097152);let end;while((end=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!line)continue;const q=JSON.parse(line),p=pending.get(q.id);assert.ok(p,'Unexpected response');for(const k of ['stdout','stderr'])if(q[k]){const s=Buffer.from(q[k],'base64').toString();p[k]+=s;assert.ok(Buffer.byteLength(p.stdout)+Buffer.byteLength(p.stderr)<=1048576);if(k==='stdout')p.onStdout?.(s);}if(q.code!==undefined||q.error){clearTimeout(p.timer);pending.delete(q.id);if(q.error)p.reject(new Error(q.error));else p.resolve({code:q.code,stdout:p.stdout,stderr:p.stderr});}}});
 return {exec(command,input='',{milliseconds=20000,onStdout}={}){assert.ok(!closed);const id=++sequence;return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{rejectAll(new Error('Owned SSH command deadline exceeded'));child.kill();},milliseconds);pending.set(id,{resolve,reject,timer,stdout:'',stderr:'',onStdout});child.stdin.write(Buffer.from(JSON.stringify({id,command,input:Buffer.from(input).toString('base64'),seconds:Math.max(1,(milliseconds-1000)/1000)})).toString('base64')+'\n');});},close(){child.stdin.end();setTimeout(()=>{if(!closed)child.kill();},2000).unref();}};
}
