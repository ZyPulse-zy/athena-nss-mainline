import fs from 'node:fs';import crypto from 'node:crypto';
import {readNormalCandidates,visible} from './normal-reader.mjs';
const root='work/resident-normal-observe-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(4).toString('hex');fs.mkdirSync(root);
try{console.log(JSON.stringify({...visible(await readNormalCandidates(root)),output:root}));}catch(e){fs.writeFileSync(root+'/failure-private.json',JSON.stringify({error:String(e),stack:String(e.stack),routerWrites:false,trafficGenerated:false})+'\n',{flag:'wx'});console.error(String(e));process.exitCode=1;}
