import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss39',sha=s=>crypto.createHash('sha256').update(s).digest('hex');
let s=fs.readFileSync(root+'/original-worker.lua','utf8');const original=s;
function once(a,b){assert.equal(s.split(a).length,2,a);s=s.replace(a,()=>b)}
const old="local function bounded(cmd,cap)\r\n assert(ramReady(false));return direct('/usr/bin/timeout -k 1 2 /bin/sh -c '..quote(cmd),cap)\r\nend";
const anchor=original.includes(old)?old:old.replaceAll('\r\n','\n');
once(anchor,'local TCCommand=(function()\n'+fs.readFileSync(root+'/tc-command.lua','utf8')+'\nend)()\nlocal function bounded(argv,cap)\n assert(ramReady(false));locksForCommand();return TCCommand.run(n,now,argv,cap)\nend');
// The existing locks() declaration occurs below bounded(); resolve it after definition.
once('local TCCommand=(function()','local locksForCommand\nlocal TCCommand=(function()');
once('local function activeOwner()','locksForCommand=locks\nlocal function activeOwner()');
once("bounded('/sbin/tc -j qdisc show dev '..dev,65536)","bounded({'-j','qdisc','show','dev',dev},65536)");
once("bounded('/sbin/tc -d filter show dev '..dev..' parent '..h,262144)","bounded({'-d','filter','show','dev',dev,'parent',h},262144)");
once("pcall(bounded,'/sbin/tc -batch '..p,65536)","pcall(bounded,{'-batch',p},65536)");
once(" local rc=os.execute(base..'/group-runner 6 /bin/sh -c '"," local mutationBegan=now()\n local rc=os.execute(base..'/group-runner 6 /bin/sh -c '");
once("assert(rc==0,'Classifier mutation child failed')","assert(rc==0,'Classifier mutation child failed; action='..action..'; rawStatus='..tostring(rc)..'; elapsed='..tostring(now()-mutationBegan))");
fs.writeFileSync(root+'/worker.lua',s);
fs.writeFileSync(root+'/candidate-manifest.json',JSON.stringify({oldWorkerSha256:sha(original),workerSha256:sha(s),tcCommandSha256:sha(fs.readFileSync(root+'/tc-command.lua')),onlyChanges:['replace detached tc timeout with direct child supervision in existing mutation group','validate exact tc argument shapes and lock ownership','include mutation action raw exit status and elapsed time'],boundsUnchanged:{tcSeconds:2,mutationSeconds:6,publicationFreshness:true,sourceBytes:524288},failedCommandStillFatal:true,installed:false},null,2)+'\n');
console.log(JSON.stringify({built:true,workerSha256:sha(s),installed:false}));
