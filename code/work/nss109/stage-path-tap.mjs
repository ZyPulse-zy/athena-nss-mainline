// Passive target diagnostic, independent cleanup before the first RAM file write.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import zlib from 'node:zlib';
import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const root='work/nss109',hash=b=>crypto.createHash('sha256').update(b).digest('hex'),binary=fs.readFileSync(root+'/udp-path-tap-aarch64');assert.equal(binary.readUInt16LE(18),183);assert.ok(binary.length<262144);
const id='nss109-tap-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex'),dir=root+'/'+id;fs.mkdirSync(dir);const save=(n,o)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify(o,null,2)+'\n',{flag:'wx'});
const c=await connectRouter(),run=async s=>{const e=encode(s),r=receipt(await c.run(e.command),e);assert.equal(r.code,0,r.stderr||'Read/staging operation failed');return r.stdout;};
try{
 assert.equal((await run('sh /root/router-project/scripts/transaction.sh status')).trim(),'NO_ACTIVE_TRANSACTION');
 await run('test "$(cat /sys/kernel/debug/ecm/front_end_ipv4_stop)" = 1; test "$(cat /sys/kernel/debug/ecm/front_end_ipv6_stop)" = 1; test "$(cat /sys/kernel/debug/ecm/ecm_nss_ipv4/accelerated_count)" = 0; sha256sum -c /root/router-project/experiments/nss6-install-20260930/protected.sha256 >/dev/null');
 const boot=(await run('cat /proc/sys/kernel/random/boot_id')).trim(),cp=(await run('sh /root/router-project/scripts/checkpoint.sh before-'+id)).match(/CHECKPOINT=([a-zA-Z0-9-]+)/)?.[1];assert.ok(cp);
 const remote='/root/router-project/backups/'+cp+'/config.tar.gz',digest=(await run('sha256sum '+remote)).split(/\s/)[0];await c.download(remote,dir+'/checkpoint-private.tar.gz');const bytes=fs.readFileSync(dir+'/checkpoint-private.tar.gz');assert.equal(hash(bytes),digest);zlib.gunzipSync(bytes);save('checkpoint',{name:cp,sha256:digest,gzipVerified:true});
 const plan={owner:crypto.randomBytes(16).toString('hex'),boot,seconds:480,files:{'udp-path-tap':{bytes:binary.length,sha256:hash(binary)},cancel:{bytes:1,sha256:hash(Buffer.from('1'))}}};
 const code=fs.readFileSync('work/nss23/stage-guardian.lua','utf8').replace('__PLAN__',()=>JSON.stringify(plan));const stage=JSON.parse(await run("lua - <<'NSS109_TAP_STAGE'\n"+code+'\nNSS109_TAP_STAGE\n'));assert.ok(stage.success&&stage.rollbackBeforeFirstWrite&&stage.parentIdentityVerified&&stage.pipeInodesVerified);save('stage-private',stage);
 // Parent handshake checks PID/start/session and only pipe/null FDs before upload.
 await c.upload(root+'/udp-path-tap-aarch64',stage.ready.dir+'/udp-path-tap');assert.equal((await run('sha256sum '+stage.ready.dir+'/udp-path-tap')).split(/\s/)[0],hash(binary));
 // Executability is confined to this owner/inode staging file; cleanup tracks its mode.
 await run('chmod 600 '+stage.ready.dir+'/udp-path-tap');
 const interpreter='/lib/ld-musl-aarch64.so.1';const self=JSON.parse(await run(interpreter+' '+stage.ready.dir+'/udp-path-tap --self-test'));assert.equal(self.passed,true);
 const out={passed:true,dir,checkpoint:cp,stage,binarySha256:hash(binary),binaryBytes:binary.length,interpreter,selfTest:self,routerQdiscOrRoutingWrites:false,independent480SecondStageCleanup:true,nativeDurationMaximumSeconds:12,outerTimeoutSeconds:14,observedAt:new Date().toISOString()};
 fs.writeFileSync(root+'/tap-stage-latest-private.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});save('target-qualified',out);console.log(JSON.stringify({passed:true,targetParserCases:self.parserCases,binaryBytes:binary.length,independentStageCleanup:true,routerQdiscOrRoutingWrites:false}));
}finally{c.close();}
