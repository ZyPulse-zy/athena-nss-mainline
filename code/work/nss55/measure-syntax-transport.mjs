import fs from'node:fs';import{encode}from'../nss11/v7-observe-repair/observe2/transport.mjs';
const out=[];
for(const[name,path]of[['classifier','work/nss53/classifier.lua'],['tags','work/nss49/classified-tags.lua'],['normalizer','work/nss49/tag-normalizer.lua'],['phase','work/nss53/core-guard-phase.lua']]){
 const source=fs.readFileSync(path,'utf8');const code="/usr/bin/lua - <<'NSS16_COMPILE_ONLY'\nlocal s=[===["+source+"]===];assert(loadstring(s));print('SYNTAX_ONLY_PASS')\nNSS16_COMPILE_ONLY\n";
 let result;try{const e=encode(code);result={accepted:true,execBytes:e.execBytes};}catch(error){result={accepted:false,error:String(error)};}
 out.push({name,sourceBytes:Buffer.byteLength(source),...result});
}
fs.writeFileSync('work/nss55/syntax-transport-measurement.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(out));
