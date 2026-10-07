// Read only the failed deadline precondition; no firewall or endpoint actions.
import fs from 'node:fs';import assert from 'node:assert/strict';import {persistentSsh} from '../v27-raw/persistent-ssh.mjs';
const dir=process.argv[2];assert.match(dir,/^work\/v29-peer-proof\/run-\d{14}-[a-f0-9]{16}$/);
const r=JSON.parse(fs.readFileSync(dir+'/firewall-receipt-private.json')),ssh=persistentSsh();
try{const out=await ssh.exec('python3 -B -E -s -u -',`import json,time\nprint(json.dumps({'remainingSeconds':${r.deadline}-time.monotonic(),'readonly':True}))\n`,{milliseconds:10000});fs.writeFileSync(dir+'/deadline-diagnostic-private.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});assert.equal(out.code,0);console.log(out.stdout.trim());}finally{ssh.close();}
