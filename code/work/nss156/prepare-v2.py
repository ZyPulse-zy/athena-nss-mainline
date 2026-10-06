from pathlib import Path
r=Path(__file__).resolve().parent
def write(n,s):
    p=r/n;assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
s=(r/'raw-client.mjs').read_text(encoding='utf-8').replace("import {createPacer}","import {nextPendingPort} from './pending-policy.mjs';\nimport {createPacer}")
s=s.replace('let ended=false,client,sock,uploadTimer,','let ended=false,client,sock,uploadTimer,pendingTimer,')
s=s.replace('ended=true;clearInterval(uploadTimer);','ended=true;clearTimeout(pendingTimer);clearInterval(uploadTimer);')
s=s.replace('const old=client;clearInterval(uploadTimer);','const old=client;clearTimeout(pendingTimer);clearInterval(uploadTimer);')
s=s.replace("current.on('connect',()=>current.write(token));current.on('error',e=>{if(current===client)stop('TCP: '+e.message)});", """const attemptedAt=performance.now();
 function retryPending(reason,failed){if(current!==client||ended)return;if(authenticated){stop('TCP: '+reason);return}
  const attempt={port,reason,at:Date.now()/1000,elapsedMs:performance.now()-attemptedAt,nonceAccepted:false};
  stats.pendingTcpAttempts=(stats.pendingTcpAttempts??[]);stats.pendingTcpAttempts.push(attempt);loadOut.write(JSON.stringify({event:'pending-tcp-refused',...attempt})+'\\n');
  try{const next=nextPendingPort({start:c.tcpSourcePort,port,authenticated,elapsedMs:attempt.elapsedMs,failed});assert.ok(next!==null);connectTcp(next)}catch(e){stop(String(e))}
 }
 pendingTimer=setTimeout(()=>retryPending('Pending TCP nonce not accepted within original matching slice',false),5500);
 current.on('connect',()=>current.write(token));current.on('error',e=>retryPending(e.message,true));""")
s=s.replace("else stop('Unexpected raw TCP close')","else retryPending('Unexpected raw TCP close',true)")
s=s.replace('authenticated=true;stats.tcpConnected=true;', 'authenticated=true;clearTimeout(pendingTimer);stats.tcpConnected=true;')
s=s.replace('x.tcpSourcePort!==stats.tcpSourcePort)connectTcp', 'x.tcpSourcePort>stats.tcpSourcePort)connectTcp')
assert 'current.on(\'error\',e=>retryPending' in s;write('raw-client-v2.mjs',s)
write('start-dallas-v2.mjs',(r/'start-dallas.mjs').read_text(encoding='utf-8').replace("root+'/raw-client.mjs'","root+'/raw-client-v2.mjs'"))
write('epoch-driver-v2.mjs',(r/'epoch-driver.mjs').read_text(encoding='utf-8').replace('./session-binding.mjs','./session-binding-v2.mjs'))
s=(r/'pilot-supervisor.mjs').read_text(encoding='utf-8').replace('./session-binding.mjs','./session-binding-v2.mjs').replace('./epoch-driver.mjs','./epoch-driver-v2.mjs').replace("out=root+'/run1'","out=root+'/run2'").replace("root+'/start-dallas.mjs'","root+'/start-dallas-v2.mjs'").replace('frozen-qualified-inputs','frozen-qualified-inputs-v2').replace('entry-source-manifest.json','entry-source-manifest-v2.json')
write('pilot-supervisor-v2.mjs',s)
write('session-binding-v2.mjs',(r/'session-binding.mjs').read_text(encoding='utf-8').replace("../nss155/session-binding-v3.mjs","./session-binding.mjs").replace('entry-qualified.json','entry-qualified-v2.json'))
print('Pending nonce rotation bounded to original eight candidates; original qualified v1 bytes untouched.')
