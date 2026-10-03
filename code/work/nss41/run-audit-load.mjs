import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawn} from 'node:child_process';
import {verifyPreparation} from './session-binding.mjs';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const q=verifyPreparation(),dir='work/nss41/audit-load-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(3).toString('hex');fs.mkdirSync(dir);
const save=(n,v)=>fs.writeFileSync(dir+'/'+n+'.json',JSON.stringify(v,null,2)+'\n');
const run=(cmd,args)=>new Promise((resolve,reject)=>{const p=spawn(cmd,args,{windowsHide:true});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);p.on('error',reject);p.on('close',code=>resolve({code,stdout,stderr}));});
const code=fs.readFileSync('work/nss41/observe-publication.lua','utf8').replace('__SPEC__',()=>JSON.stringify({configSha256:q.configuration.configSha256}));
const e=encode("/usr/bin/lua - <<'NSS41_PUBLICATION_LOAD'\n"+code+"\nNSS41_PUBLICATION_LOAD\n");const c=await connectRouter();
try{
 const observation=c.run(e.command).then(r=>{const raw=receipt(r,e);save('publication-raw-private',raw);assert.equal(raw.code,0,raw.stderr);const d=JSON.parse(raw.stdout);save('publication-private',d);return d;});
 await new Promise(r=>setTimeout(r,700));save('plan',{startedAt:new Date().toISOString(),syntheticTcpDownloadOnly:true,realGameTest:false,routerConfigurationWrites:false,connections:8,maximumBytes:536870912,eachRequestDeadlineSeconds:25,officialApiSource:'https://github.com/cloudflare/speedtest/blob/main/README.md'});
 const load=run('C:/Users/lishu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['work/nss41/finite-download.py',dir]);
 await new Promise(r=>setTimeout(r,2500));
 const audits=[];
 for(let i=1;i<=3;i++){const label=dir.split('/').at(-1)+'-'+i;const startedAt=new Date().toISOString();const result=await run(process.execPath,['work/nss41/current-audit-diagnostic.mjs',label]);const audit={slot:i,label,startedAt,finishedAt:new Date().toISOString(),...result};audits.push(audit);save('audit-'+i+'-command-private',audit);await new Promise(r=>setTimeout(r,1000));}
 const download=await load;save('download-command-private',download);assert.equal(download.code,0,download.stderr);
 const observed=await observation;const result={completed:true,output:dir,audits:audits.map(a=>({slot:a.slot,exitCode:a.code})),publicationFrames:observed.frames.length,routerConfigurationWrites:false,nssOpened:false};save('result',result);fs.writeFileSync('work/nss41/audit-load-latest.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{c.close()}
