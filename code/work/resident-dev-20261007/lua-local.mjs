import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {root} from './build-classifier.mjs';

export function luaLiteral(value){
 if(typeof value==='string')return "'"+value.replaceAll('\\','\\\\').replaceAll("'","\\'").replaceAll('\n','\\n').replaceAll('\r','\\r')+"'";
 if(typeof value==='number') {if(!Number.isFinite(value))throw Error('Nonfinite Lua value');return String(value);}
 if(typeof value==='boolean')return String(value);
 if(Array.isArray(value))return'{'+value.map(luaLiteral).join(',')+'}';
 if(value&&typeof value==='object')return'{'+Object.entries(value).map(([k,v])=>'['+luaLiteral(k)+']='+luaLiteral(v)).join(',')+'}';
 throw Error('Unsupported fixture value');
}
const unix=p=>{const s=path.resolve(p).replaceAll('\\','/');if(!/^[A-Za-z]:\//.test(s))throw Error('Drive path required');return'/mnt/'+s[0].toLowerCase()+s.slice(2);};
export function executeLua(text,label){
 if(!/^[a-z0-9-]+$/.test(label))throw Error('Unsafe local test label');
 const directory=root+'/tests/'+label+'-'+Date.now()+'-'+crypto.randomBytes(4).toString('hex');
 fs.mkdirSync(directory,{recursive:true});fs.writeFileSync(directory+'/replay.lua',text,{flag:'wx'});
 const runtime='work/nss9/lua-runtime/extracted/usr';
 const result=spawnSync('wsl.exe',['-d','Athena-Cake-Build','--exec','/usr/bin/env',
  'LD_LIBRARY_PATH='+unix(runtime+'/lib/x86_64-linux-gnu'),unix(runtime+'/bin/lua5.1'),unix(directory+'/replay.lua')],
  {encoding:'utf8',windowsHide:true,timeout:30000,maxBuffer:262144});
 for(const key of ['stdout','stderr'])fs.writeFileSync(directory+'/'+key+'.txt',result[key]??'',{flag:'wx'});
 return{code:result.status,stdout:result.stdout??'',stderr:result.stderr??'',error:result.error?.code??null,directory,routerAccess:false};
}
