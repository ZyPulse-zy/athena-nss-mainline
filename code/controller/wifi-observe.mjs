// Manual SSH stdin runner for the maintained Lua observer. Installs no files.
// The local transport module owns authentication and pinned-host verification.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';

const options={seconds:'30'};
const allowed=new Set(['transport','transport-cwd','seconds','private-dir']);
for(let i=2;i<process.argv.length;i+=2){
 const name=process.argv[i]?.replace(/^--/,'');
 if(!allowed.has(name)||!process.argv[i+1])throw Error('Usage: wifi-observe.mjs --transport MODULE --transport-cwd DIR --private-dir NEW_DIR [--seconds 5..120]');
 options[name]=process.argv[i+1];
}
const seconds=Number(options.seconds);
if(!Number.isInteger(seconds)||seconds<5||seconds>120)throw Error('Duration must be 5..120 seconds');
for(const name of ['transport','transport-cwd','private-dir'])if(!options[name])throw Error('Missing --'+name);
const transport=path.resolve(options.transport),transportCwd=path.resolve(options['transport-cwd']);
const directory=path.resolve(options['private-dir']);
fs.mkdirSync(path.dirname(directory),{recursive:true});
fs.mkdirSync(directory,{mode:0o700}); // Never overwrite a previous capture.
if(process.platform==='win32'){
 const user=process.env.USERDOMAIN+'\\'+process.env.USERNAME;
 const r=spawnSync('icacls',[directory,'/inheritance:r','/grant:r',user+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F','*S-1-5-32-544:(OI)(CI)F'],{windowsHide:true});
 if(r.status!==0)throw Error('Cannot protect private observation directory');
}
const base=path.join(path.dirname(fileURLToPath(import.meta.url)),'native');
const files=Object.fromEntries(['wifi.lua','wifi_collect.lua','wifi-diagnose.lua'].map(name=>[name,fs.readFileSync(path.join(base,name),'utf8')]));
const source="arg={[0]='-',[1]='"+seconds+"'}\n"+
 "package.loaded['athena.wifi']=(function()\n"+files['wifi.lua']+'\nend)()\n'+
 "package.loaded['athena.wifi_collect']=(function()\n"+files['wifi_collect.lua']+'\nend)()\n'+
 "package.loaded['athena.wifi_private_sink']=function(raw,report)print(require('luci.jsonc').stringify({raw=raw,report=report}))end\n"+
 files['wifi-diagnose.lua'];
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
process.chdir(transportCwd);
const adapter=await import(pathToFileURL(transport));
const connection=await adapter.connect();
try{
 const started=performance.now();
 let result;
 if(typeof connection.runStdin==='function'){
  // Keep source out of the SSH exec request: Dropbear bounds command length.
  result=await connection.runStdin('timeout -k 2 '+(seconds+45)+' lua -',source);
 }else{
  const compressed=zlib.gzipSync(source,{level:9}).toString('base64');
  const command="printf '%s' '"+compressed+"' | openssl base64 -d -A | gzip -dc | timeout -k 2 "+(seconds+45)+" lua -";
  if(Buffer.byteLength(command)>8000)throw Error('Transport must provide runStdin(command, source) for this source bundle; no observation started');
  result=await connection.run(command);
 }
 fs.writeFileSync(path.join(directory,'transport-private.json'),JSON.stringify(result),{mode:0o600});
 if(result.code!==0)throw Error('Observer failed; private result retained. Exit '+result.code);
 const data=JSON.parse(result.stdout);
 data.report.capturedAt=new Date().toISOString();data.report.processSeconds=(performance.now()-started)/1000;
 data.report.streamedWithoutInstallation=true;data.report.sourceBundleSha256=sha(source);
 data.report.sourceFiles=Object.fromEntries(Object.entries(files).map(([name,text])=>[name,sha(text)]));
 fs.writeFileSync(path.join(directory,'raw-private.json'),JSON.stringify(data.raw,null,2),{mode:0o600});
 fs.writeFileSync(path.join(directory,'summary.json'),JSON.stringify(data.report,null,2),{mode:0o600});
 console.log(JSON.stringify({capturedAt:data.report.capturedAt,privateDirectory:directory,
  report:path.join(directory,'summary.json'),seconds:data.report.elapsedSeconds,
  queryCount:data.report.queries.length,maxQuerySeconds:Math.max(...data.report.queries.map(q=>q.seconds)),
  topology:data.report.topology,installed:false}));
}finally{connection.close()}
