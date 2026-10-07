import fs from'node:fs';import crypto from'node:crypto';import{spawnSync}from'node:child_process';
const root='work/v31-normal',dir=root+'/run-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(dir);
const out=fs.openSync(dir+'/controller-stdout-private.txt','wx'),err=fs.openSync(dir+'/controller-stderr-private.txt','wx');
fs.writeFileSync(root+'/active-run-private.json',JSON.stringify({directory:dir,startedAt:new Date().toISOString(),singleApplicationSession:true})+'\n',{flag:'wx'});
let result;try{result=spawnSync(process.execPath,[root+'/session.mjs','session'],{windowsHide:true,stdio:['ignore',out,err],timeout:310000});}finally{fs.closeSync(out);fs.closeSync(err);}
const summary={finishedAt:new Date().toISOString(),exitCode:result.status,signal:result.signal,error:result.error?.code??null,privateOutputsPreserved:true};fs.writeFileSync(dir+'/controller-process.json',JSON.stringify(summary,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(summary));if(result.status!==0)process.exitCode=1;
