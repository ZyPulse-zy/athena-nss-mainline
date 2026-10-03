// Derive the same independently qualified deployment/undo procedure; one source change.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/nss37';const old=JSON.parse(fs.readFileSync('work/nss35/deployment-latest.json'));assert.equal(old.committed,true);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const original=JSON.parse(fs.readFileSync(root+'/original-manifest.json'));assert.equal(original.configSha256,old.configHash);
const local=JSON.parse(fs.readFileSync(root+'/normalizer-qualified.json')),native=JSON.parse(fs.readFileSync(root+'/native-normalizer-qualified.json'));
assert.ok(local.passed&&native.passed&&native.results.every(r=>r.allOutputsEqual&&r.cpuReductionPercent>20));
assert.equal(local.sourceSha256,sha(fs.readFileSync(root+'/conntrack-source.lua')));assert.equal(native.sourceSha256,local.sourceSha256);
for(const n of ['worker.lua','guardian.lua']){const b=fs.readFileSync(root+'/original-'+n);assert.equal(sha(b),original.files[n]);fs.writeFileSync(root+'/'+n,b);}
let upgrade=fs.readFileSync('work/nss35/upgrade.mjs','utf8');
const begin=upgrade.indexOf("const root='work/nss35'"),end=upgrade.indexOf("const id='nss35-");assert.ok(begin>0&&end>begin);
const header=[
 "const root='work/nss37',old=JSON.parse(fs.readFileSync('work/nss35/deployment-latest.json')),sha=b=>crypto.createHash('sha256').update(b).digest('hex'),json=o=>JSON.stringify(o,null,2)+'\\n';assert.equal(old.committed,true);",
 "const qualified=JSON.parse(fs.readFileSync(root+'/normalizer-qualified.json')),native=JSON.parse(fs.readFileSync(root+'/native-normalizer-qualified.json')),life=JSON.parse(fs.readFileSync(root+'/lifecycle-qualified.json'));",
 "assert.ok(qualified.passed&&native.passed&&life.passed);for(const q of [qualified,native])assert.equal(q.sourceSha256,sha(fs.readFileSync(root+'/conntrack-source.lua')));assert.equal(life.ctSourceSha256,qualified.sourceSha256);assert.ok(native.results.every(r=>r.allOutputsEqual&&r.cpuReductionPercent>20));",
 "const previousConfig=JSON.parse(fs.readFileSync(old.localDir+'/config.json'));for(const n of ['worker.lua','guardian.lua'])assert.equal(sha(fs.readFileSync(root+'/'+n)),previousConfig.files[n]);",
 ""
].join('\n');
upgrade=upgrade.slice(0,begin)+header+upgrade.slice(end).replace("const id='nss35-'","const id='nss37-'");
const anchor="const newCfg=Buffer.from(json(cfg)),newHash=sha(newCfg);";
assert.equal(upgrade.split(anchor).length,2);
upgrade=upgrade.replace(anchor,()=>"const normalized=structuredClone(cfg);normalized.files['conntrack-source.lua']=previousConfig.files['conntrack-source.lua'];normalized.installTransaction=previousConfig.installTransaction;assert.deepEqual(normalized,previousConfig,'Only attribute extraction may change');"+anchor);
upgrade=upgrade.replace('boundedAddressRecoveryTrial:true','attributeNormalizerTrial:true');
fs.writeFileSync(root+'/upgrade.mjs',upgrade);
for(const n of ['observe-compact.mjs','verify-rollback.mjs']){
 fs.writeFileSync(root+'/'+n,fs.readFileSync('work/nss35/'+n,'utf8').replaceAll('work/nss35','work/nss37'));
}
fs.writeFileSync(root+'/deployment-audit.mjs',fs.readFileSync('work/nss35/operational-audit.mjs','utf8').replaceAll('work/nss35','work/nss37'));
let life=fs.readFileSync('work/nss36/test-lifecycle.py','utf8');
life=life.replace("core=src('classifier-core.lua');ct=src('conntrack-source.lua');backend=src('backend.lua')","core=src('classifier-core.lua');ct=(here/'conntrack-source.lua').read_text();backend=src('backend.lua')\nassert hashlib.sha256(ct.encode()).hexdigest()==json.loads((here/'normalizer-qualified.json').read_text())['sourceSha256']");
life=life.replace("'ctSourceSha256':cfg['files']['conntrack-source.lua']","'ctSourceSha256':hashlib.sha256(ct.encode()).hexdigest()").replace('Exact deployed core, actual CT normalization and actual leaf function.','Unchanged deployed core and leaf function with candidate CT normalization.');
fs.writeFileSync(root+'/test-lifecycle.py',life);
let commit=fs.readFileSync('work/nss35/commit-channel.mjs','utf8').replaceAll('work/nss35','work/nss37').replaceAll('address-trial-qualified.json','normalizer-trial-qualified.json');
commit=commit.replace('boundedAddressRecovery=true','equivalentAttributeNormalizer=true');
const guard="assert.equal(trial.workerSha256,JSON.parse(fs.readFileSync(ctx.localDir+'/config.json')).files['worker.lua']);";
assert.ok(commit.includes(guard));commit=commit.replace(guard,()=>guard+"assert.equal(trial.sourceSha256,JSON.parse(fs.readFileSync(ctx.localDir+'/config.json')).files['conntrack-source.lua']);");
fs.writeFileSync(root+'/commit-channel.mjs',commit);
console.log(JSON.stringify({prepared:true,workerGuardianUnchanged:true,onlyNormalizerAndConfigHashChanged:true,routerWrites:false}));
