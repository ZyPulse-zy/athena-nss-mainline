import fs from 'node:fs';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const active=read('work/v57-resident-bootstrap/active-private.json'),root=active.runtimeRoot,out={state:active.state};
if(fs.existsSync(root+'/load-latest-private.json')){const load=read(root+'/load-latest-private.json'),s=read(load.dir+'/status-private.json');for(const key of ['elapsed','tcpConnected','udpSent','udpReceived','errors'])out[key]=s[key];if(fs.existsSync(load.dir+'/matching-private.json')){const a=read(load.dir+'/matching-private.json');out.matchingReads=a.length;out.lastMatchingCode=a.at(-1).code;out.lastAcquisition=a.at(-1).acquisition;}}
if(fs.existsSync(root+'/pilot-reference-private.json')){const p=read(root+'/pilot-reference-private.json').directory;out.nativeOwnerStarted=fs.existsSync(p+'/detached-owner-reference-private.json');if(fs.existsSync(p+'/automatic-result.json'))out.pilotResult=read(p+'/automatic-result.json');}
console.log(JSON.stringify(out));
