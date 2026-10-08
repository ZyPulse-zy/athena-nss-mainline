import fs from 'node:fs';
import assert from 'node:assert/strict';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
import {verifyDeployment} from '../resident-dev-20261007/deployment-binding.mjs';

const originalPath='work/nss49/read-prerequisites.lua';
const originalCommand="local function cmd(c)local f=assert(io.popen('/usr/bin/timeout -k 1 3 '..c..' 2>&1; rc=$?;printf \"\\n__NSS20_RC__%s\\n\" \"$rc\"'));local s=f:read('*a');f:close();local b,r=s:match('^(.*)\\n__NSS20_RC__(%d+)\\n$');assert(b and r=='0',b);return b end";
const quote=s=>"'"+s.replaceAll("'","'\\''")+"'";

// The original checks and fields stay intact. Read command stdout in the shell,
// whose exit status is retained by the SSH receipt, rather than Lua io.popen.
// This avoids dereferencing a nil FILE* read and never substitutes empty output
// or retries a failed command. Every original command still has its 3s deadline.
export function prerequisiteLua(source){
 const normalized=source.replaceAll('\r\n','\n');
 assert.equal(normalized.split(originalCommand).length,2,'Original prerequisite command helper changed');
 const replacement="assert(#arg==6,'Missing prerequisite command output');local outputs={['/sbin/ip -j -d link show dev '..interface]=arg[2],['/bin/ubus call network.interface.'..service..' status']=arg[3],['/usr/bin/sha256sum /root/router-project/experiments/nss9-abg3-20261001/eap-header']=arg[4],['/usr/bin/sha256sum /root/router-project/scripts/core-guard.sh']=arg[5],['/usr/bin/sha256sum /root/router-project/scripts/prepare-macvlans.sh']=arg[6]};local function cmd(c)local s=assert(outputs[c],'Unexpected prerequisite command');assert(type(s)=='string' and #s>0 and #s<=65536,'Missing or oversized prerequisite output');return s end";
 return normalized.replace(originalCommand,()=>replacement);
}
export function prerequisiteShell(wan,source){
 assert.ok(Number.isInteger(wan)&&wan>=1&&wan<=5,'Invalid WAN');
 const lua=prerequisiteLua(source),marker='ATHENA_PREREQUISITE_READ_ONLY';
 assert.ok(!lua.includes(marker),'Heredoc delimiter collision');
 return `set -eu
nss_mode=$(/usr/bin/timeout -k 1 3 /sbin/ip -j -d link show dev rpwan${wan})
nss_status=$(/usr/bin/timeout -k 1 3 /bin/ubus call network.interface.wan${wan} status)
nss_eap=$(/usr/bin/timeout -k 1 3 /usr/bin/sha256sum /root/router-project/experiments/nss9-abg3-20261001/eap-header)
nss_core=$(/usr/bin/timeout -k 1 3 /usr/bin/sha256sum /root/router-project/scripts/core-guard.sh)
nss_prepare=$(/usr/bin/timeout -k 1 3 /usr/bin/sha256sum /root/router-project/scripts/prepare-macvlans.sh)
exec /usr/bin/lua - ${wan} "$nss_mode" "$nss_status" "$nss_eap" "$nss_core" "$nss_prepare" <<'${marker}'
${lua}
${marker}
`;
}
export function prerequisiteCommand(wan,source,base){
 assert.match(base,/^\/[A-Za-z0-9_./-]+$/);
 return base+'/group-runner 6 /bin/sh -c '+quote(prerequisiteShell(wan,source));
}
export async function readPrerequisites(c,dir,selected,options={}){
 assert.match(dir,/^work\/resident-rc1-run-\d{14}-[a-f0-9]{8}\/session-\d{14}-[a-f0-9]{8}$/);
 const source=options.source??fs.readFileSync(originalPath,'utf8');
 const base=options.base??verifyDeployment().deployment.base;
 const rows=[];
 for(const slot of ['tcp','udp','tcp2']){
  const flow=selected[slot];assert.ok(flow&&Number.isInteger(flow.wan));
  if(rows.some(q=>q.wan===flow.wan))continue;
  const encoded=encode(prerequisiteCommand(flow.wan,source,base));
  const raw=receipt(await c.run(encoded.command),encoded);
  fs.writeFileSync(dir+'/prerequisites-'+slot+'-raw-private.json',JSON.stringify(raw,null,2)+'\n',{flag:'wx'});
  assert.equal(raw.code,0,'WAN prerequisite command refused; raw receipt retained');
  assert.ok(typeof raw.stdout==='string'&&Buffer.byteLength(raw.stdout)<=65536,'Invalid or oversized prerequisite response');
  const row=JSON.parse(raw.stdout);
  assert.equal(row.wan,flow.wan);assert.equal(row.status['ipv4-address'][0].address,flow.reply.dst);
  assert.equal(row.status.l3_device,'rpwan'+flow.wan);
  fs.writeFileSync(dir+'/prerequisites-'+slot+'-private.json',JSON.stringify(row,null,2)+'\n',{flag:'wx'});
  rows.push(row);
 }
 return rows;
}
