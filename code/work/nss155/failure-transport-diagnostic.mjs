import fs from 'node:fs';import assert from 'node:assert/strict';import {spawnSync} from 'node:child_process';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss155',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),config=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),status=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));
assert.equal(status.session,config.session);assert.ok(Number.isInteger(status.tcpSourcePort)&&status.tcpSourcePort>=config.tcpSourcePort&&status.tcpSourcePort<config.tcpSourcePort+8);
assert.equal(config.tcpServerAddress,'18.138.159.236');const client=config.clientAddress;assert.equal(client,'192.168.237.207');
const c=await connectRouter();try{
 const cmd='conntrack -L -f ipv4 -p tcp -s '+client+' -d '+config.tcpServerAddress+' --sport '+status.tcpSourcePort+' --dport 22 -o extended,id';
 const e=encode(cmd),raw=receipt(await c.run(e.command),e);fs.writeFileSync(load.dir+'/failed-transport-ct-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0);
 const rows=raw.stdout.trim().split(/\r?\n/).filter(Boolean);const states=rows.map(s=>({state:s.match(/\b(ESTABLISHED|SYN_SENT|SYN_RECV|TIME_WAIT|CLOSE_WAIT|FIN_WAIT|CLOSE|LAST_ACK)\b/)?.[1]??'UNKNOWN',wan:Number(s.match(/\bmark=(\d+)/)?.[1]??0)>>>16&255}));
 const remote=spawnSync('ssh',['-o','BatchMode=yes','-o','ConnectTimeout=8','sg','uptime'],{encoding:'utf8',windowsHide:true,timeout:12000});
 const result={observedAt:new Date().toISOString(),readonly:true,targetCtRows:rows.length,states,remoteReadonlySshReachable:remote.status===0,remoteLoadOutput:remote.stdout.trim(),clientFailureWasKeepaliveTimeout:true,rootCauseProven:false,routerNssExperimentStarted:false};
 fs.writeFileSync(load.dir+'/transport-diagnostic.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
}finally{c.close()}
