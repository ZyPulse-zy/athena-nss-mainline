"""Reconstruct exact uninstalled candidates in target RAM under existing caps."""
from pathlib import Path
import difflib,hashlib,json,subprocess
here=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
sources={}
for name in ['worker.lua','guardian.lua']:
    original=(here/('original-'+name)).read_text();candidate=(here/('stale-'+name)).read_text()
    a=original.splitlines(keepends=True);b=candidate.splitlines(keepends=True)
    patches=[]
    for group in difflib.SequenceMatcher(None,a,b,autojunk=False).get_grouped_opcodes(3):
        first,last=group[0],group[-1]
        old=''.join(a[first[1]:last[2]]);new=''.join(b[first[3]:last[4]])
        assert original.count(old)==1
        patches.append([old,new])
    rebuilt=original
    for old,new in patches:
        assert rebuilt.count(old)==1;rebuilt=rebuilt.replace(old,new)
    assert rebuilt==candidate
    sources[name]={'originalSha256':sha(original.encode()),'candidateSha256':sha(candidate.encode()),'patches':patches}
(here/'stale-native-patches.json').write_text(json.dumps(sources,indent=2)+'\n',encoding='utf-8')
script=r'''// Exact reconstruction and pure replay. No candidate installation or native mutation.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {verifyPreparation} from '../nss42/session-binding.mjs';import {connectRouter} from '../nss20/connect-router.mjs';
import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
verifyPreparation();const root='work/nss45',mode=process.argv[2]??'syntax';assert.ok(['syntax','replay'].includes(mode));
const d=JSON.parse(fs.readFileSync('work/nss39/deployment-latest.json')),cfg=JSON.parse(fs.readFileSync(d.localDir+'/config.json'));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex'),patches=JSON.parse(fs.readFileSync(root+'/stale-native-patches.json'));
const payloads=[],hashes={};
if(mode==='syntax')for(const[name,p]of Object.entries(patches)){
 assert.equal(p.originalSha256,cfg.files[name]);assert.equal(p.candidateSha256,sha(fs.readFileSync(root+'/stale-'+name)));hashes[name]=p.candidateSha256;
 let code="local j=require('luci.jsonc');local f=assert(io.open('"+d.base+'/'+name+"'));local s=f:read(65537);f:close();assert(#s<=65536)\nlocal function replace(a,b)local x,y=s:find(a,1,true);assert(x and not s:find(a,y+1,true));s=s:sub(1,x-1)..b..s:sub(y+1)end\n";
 for(const[a,b]of p.patches){assert.ok(!a.includes(']=======]')&&!b.includes(']=======]'));code+='replace([=======['+a+']=======],[=======['+b+']=======])\n'}
 code+="assert(loadstring(s));print(j.stringify({passed=true,checks=1,compiledSource=s}))";payloads.push({name,code});
}else{const code=fs.readFileSync(root+'/stale-replay.lua','utf8');hashes['stale-replay.lua']=sha(code);payloads.push({name:'replay',code})}
const capsules=payloads.map(({name,code})=>({name,e:encode(d.base+'/group-runner 6 /usr/bin/lua - <<\'NSS45_STALE_RAM\'\n'+code+'\nNSS45_STALE_RAM\n')}));
assert.ok(capsules.every(x=>x.e.execBytes<=9000));
const c=await connectRouter();try{
 const h=await c.run('/usr/bin/sha256sum '+d.base+'/config.json '+d.base+'/group-runner '+Object.keys(patches).map(n=>d.base+'/'+n).join(' '));assert.equal(h.code,0);
 const rows=h.stdout.trim().split('\n').map(s=>s.split(/\s/)[0]);assert.deepEqual(rows,[d.configHash,cfg.files['group-runner'],...Object.keys(patches).map(n=>cfg.files[n])]);
 let checks=0;for(const{name,e}of capsules){const r=receipt(await c.run(e.command),e);fs.writeFileSync(root+'/stale-native-'+mode+'-'+name+'-raw-private.json',JSON.stringify(r,null,2)+'\n');assert.equal(r.code,0,r.stderr);
  if(mode==='syntax'){const x=JSON.parse(r.stdout);assert.ok(x.passed);assert.equal(sha(x.compiledSource),hashes[name]);checks+=x.checks}
  else{checks+=r.stdout.split('\n').filter(s=>s.startsWith('PASS ')).length;assert.ok(r.stdout.includes('COMPLETE 34'))}
 }
 assert.equal(checks,mode==='syntax'?2:34);
 const out={passed:true,mode,checks,observedAt:new Date().toISOString(),sourceHashes:hashes,execBytes:Math.max(...capsules.map(x=>x.e.execBytes)),routerWrites:false,installed:false,realNativeLua:true,mockedNativeRecovery:mode==='replay',hardwareLifecycleQualified:false};
 fs.writeFileSync(root+'/stale-native-'+mode+'-qualified.json',JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
}finally{c.close()}
'''
(here/'check-stale-native.mjs').write_text(script,encoding='utf-8',newline='\n')
node='C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
r=subprocess.run([node,'--check',str(here/'check-stale-native.mjs')],capture_output=True,text=True,timeout=20);assert r.returncode==0,r.stderr
proof={'passed':True,'syntaxSources':len(sources),'candidateBytesReconstructedExactly':True,'replayCases':34,'noRouterWrites':True,'installed':False,'sourceSha256':sha(script.encode()),'patchesSha256':sha((here/'stale-native-patches.json').read_bytes())}
(here/'stale-native-prepared.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))
