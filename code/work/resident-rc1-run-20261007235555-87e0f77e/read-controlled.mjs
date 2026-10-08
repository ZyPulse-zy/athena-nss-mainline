import fs from'node:fs';import{readNormalCandidates,visible}from'../resident-normal-dev-20261008/normal-reader.mjs';
const root='work/resident-rc1-run-20261007235555-87e0f77e',scopePath=root+'/normal-scope-private.json';
try{const frame=await readNormalCandidates(root,{scope:fs.existsSync(scopePath)?JSON.parse(fs.readFileSync(scopePath)):undefined});console.log(JSON.stringify(visible(frame)));}catch(e){console.error(String(e));process.exitCode=1;}
