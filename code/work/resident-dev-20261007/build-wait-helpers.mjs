import fs from 'node:fs';import assert from 'node:assert/strict';import {root} from './build-classifier.mjs';
for(const name of ['wait-ready-candidate.mjs','wait-publication-metadata.mjs']){
 let s=fs.readFileSync('work/nss122/'+name,'utf8');
 if(name==='wait-ready-candidate.mjs'){assert.equal(s.split('../nss68/deployment-binding.mjs').length,2);s=s.replace('../nss68/deployment-binding.mjs','./deployment-binding.mjs');}
 s=s.replaceAll('work/nss122/'+name,root+'/'+name).replaceAll("'work/nss122/'+label","'"+root+"/'+label");
 for(const value of ['raw','out'])s=s.replaceAll("JSON.stringify("+value+",null,2)+'\\n');","JSON.stringify("+value+",null,2)+'\\n',{flag:'wx'});");
 fs.writeFileSync(root+'/'+name,s,{flag:'wx'});
}
console.log(JSON.stringify({passed:true,copiedHelpers:2,routerAccess:false}));
