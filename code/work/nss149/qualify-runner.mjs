import fs from 'node:fs';import {spawnSync} from 'node:child_process';
const v=process.argv[2];if(!/^v\d+$/.test(v??''))throw Error('Unique qualification version required');
const p=spawnSync(process.execPath,['work/nss149/qualify.mjs',v],{encoding:'utf8',windowsHide:true,timeout:60000});
fs.writeFileSync('work/nss149/qualification-'+v+'-raw-private.json',JSON.stringify({code:p.status,stdout:p.stdout,stderr:p.stderr},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({version:v,code:p.status,summary:p.stdout.trim(),failure:p.status===0?null:p.stderr.split('\n').filter(s=>/AssertionError|Error:|at file:/.test(s)).slice(0,3),fullFailurePreserved:true}));
process.exitCode=p.status??1;
