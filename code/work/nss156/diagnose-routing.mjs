import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss156',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),cfg=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json'));
const cmd='conntrack -L -f ipv4 -s '+cfg.clientAddress+' -d '+cfg.serverAddress+' -o extended,id; nft -a list table inet fw4';
const c=await connectRouter();try{const e=encode(cmd),raw=receipt(await c.run(e.command),e);fs.writeFileSync(load.dir+'/routing-diagnostic-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);
const rows=raw.stdout.split(/\r?\n/).filter(s=>/^(tcp|udp)\s/.test(s));const own=rows.filter(s=>{const ports=[...s.matchAll(/sport=(\d+)/g)].map(m=>Number(m[1]));return s.startsWith('udp')?ports[0]===cfg.udpSourcePort:ports[0]>=cfg.tcpSourcePort&&ports[0]<cfg.tcpSourcePort+8});
const states=own.map(s=>({protocol:s.split(/\s/)[0],wan:Number(s.match(/\bmark=(\d+)/)?.[1]??0)>>>16&255,state:s.match(/\b(ESTABLISHED|SYN_SENT|SYN_RECV|TIME_WAIT|CLOSE_WAIT|FIN_WAIT|CLOSE|LAST_ACK)\b/)?.[1]??'UDP',assured:s.includes('[ASSURED]')}));
const routingLines=raw.stdout.split(/\r?\n/).filter(s=>/sticky|jhash|numgen|symhash|mwan.*set|mwan.*mark/i.test(s));
const remote=spawnSync('ssh',['-o','BatchMode=yes','-o','ConnectTimeout=8','sub2api-dallas','journalctl -u '+load.unit+'.service -n 30 --no-pager -o cat'],{encoding:'utf8',windowsHide:true,timeout:12000});fs.writeFileSync(load.dir+'/endpoint-journal-private.json',JSON.stringify({code:remote.status,stdout:remote.stdout,stderr:remote.stderr},null,2)+'\n',{flag:'wx'});assert.equal(remote.status,0,remote.stderr);
const out={readonly:true,ownCtStates:states,routingHashSourceLines: routingLines,endpointHadThreadException:/Traceback|Exception in thread/.test(remote.stdout),handshakeTimeoutRootCauseProven:false};
fs.writeFileSync(load.dir+'/routing-diagnostic-private.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({readonly:true,ownCtStates:states,endpointHadThreadException:out.endpointHadThreadException,routingHashLineCount:routingLines.length,routerWrites:false,rootCauseProven:false}));
}finally{c.close()}
