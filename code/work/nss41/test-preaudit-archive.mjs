// Run the actual controller ordering with substituted IO at the audit boundary.
// Fake fixture identities never enter a router or the native gate.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {pathToFileURL} from 'node:url';import {spawnSync} from 'node:child_process';
const root=process.cwd(),here=path.join(root,'work/nss41'),actual=fs.readFileSync(path.join(here,'real-session.mjs'),'utf8');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const base=path.join(here,'archive-fixtures-'+new Date().toISOString().replace(/\D/g,'').slice(0,14)+'-'+crypto.randomBytes(3).toString('hex'));fs.mkdirSync(base);
const source='bound fixture source, no executable router payload\n',sourceHash=hash(source);
const identity=(p,id,port)=>{const original={src:'192.168.237.207',dst:'198.51.100.50',sport:port,dport:p===17?27015:443},reply={src:original.dst,dst:'192.0.2.10',sport:original.dport,dport:port};const mark=0x10000;return{key:[1,mark,p===17?'udp':'tcp',original.src,original.sport,reply.src,reply.dst,reply.sport,reply.dport,0,id].join('|'),identity:{protocolNumber:p,connectionId:id,wan:1,mark,zone:0,original,reply},decision:{class:p===17?'RT':'BULK',budgetAdmitted:true,pps:50,rateKbps:5000}};};
const cases=[];
for(const scenario of ['audit-refusal','tampered-application','no-application-pair']){
 const dir=path.join(base,scenario);fs.mkdirSync(dir);const put=(f,v)=>{const dst=path.join(dir,f);fs.mkdirSync(path.dirname(dst),{recursive:true});fs.writeFileSync(dst,typeof v==='string'?v:JSON.stringify(v));};
 put('fixture-source.txt',source);
 put('work/nss39/mainline-preflight-qualified.json',{passed:true,phasedIntegration:true});put('work/nss39/wan-scope.lua','fixture\n');put('work/nss27/wan-scope-qualified.json',{passed:true,sourceSha256:hash('fixture\n')});
 for(const [name,proof,key] of [['fast-path.lua','aba-qualified.json','sourceSha256'],['classifier.lua','consumer-qualified.json','adapterSha256']]){put('work/nss39/'+name,'fixture\n');put('work/nss39/'+proof,{passed:true,[key]:hash('fixture\n')});}
 const candidates={game:scenario==='no-application-pair'?[]:[identity(17,1001,30001)],bulk:scenario==='no-application-pair'?[]:[identity(6,1002,30002)],producer:'fixture-worker',sourceSequence:10};put('work/nss41/real-candidates-private.json',candidates);
 const appdir='work/nss41/immutable-application';const app={passed:true,directory:appdir,manifest:{}};
 for(const name of ['pc-app-endpoints-private.json','real-candidates-raw-private.json','real-candidates-private.json','real-reader-qualified.json']){const value=name==='real-candidates-private.json'?JSON.stringify(candidates):JSON.stringify({fixture:name});put(appdir+'/'+name,value);app.manifest[name]=hash(value);}
 put('work/nss41/recorded-application-latest.json',app);
 if(scenario==='tampered-application')put(appdir+'/real-reader-qualified.json','tampered fixture\n');
 let body=actual;const replace=(from,to)=>{assert.ok(body.includes(from),'Fixture replacement missing: '+from);body=body.replace(from,to);};
 replace("import {verifyPreparation} from './session-binding.mjs';",`function verifyPreparation(){return{sourceManifest:{'fixture-source.txt':'${sourceHash}'}};}`);
 for(const [file,relative] of [['pair-policy.mjs','nss39'],['flow-selection.mjs','nss27']])replace(`'../${relative}/${file}'`,JSON.stringify(pathToFileURL(path.join(root,'work',relative,file)).href));
 replace("import {validateAcceleratedState} from '../nss25/parse-ecm.mjs';",'const validateAcceleratedState=()=>{throw Error("Unexpected native acceleration call")};');
 replace("import {beginStage,uploadStage,readStage,waitStageUndo} from '../nss39/module-stage.mjs';",'const beginStage=async()=>{throw Error("Unexpected staging mutation")},uploadStage=beginStage,readStage=beginStage,waitStageUndo=beginStage;');
 replace("import {connectRouter} from '../nss27/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';",'const connectRouter=async()=>{fs.appendFileSync("events.txt","router-connect\\n");throw Error("Unexpected router connection")};const encode=()=>{throw Error("Unexpected native command")},receipt=encode;');
 replace("import {readBaseline,auditBaseline} from '../nss15/baseline.mjs';import {packetTemplate} from '../nss16/automatic-leaf-plan.mjs';",'const readBaseline=async()=>{throw Error("Unexpected checkpoint read")},auditBaseline=readBaseline,packetTemplate=()=>{throw Error("Unexpected packet tags")};');
 replace("function runNode(file,args=[]){const p=spawnSync(process.execPath,[file,...args],{encoding:'utf8',windowsHide:true,timeout:30000});assert.equal(p.status,0,p.stderr);return p.stdout.trim();}",`function runNode(file,args=[]){fs.appendFileSync('events.txt',file+'\\n');if(file.endsWith('/record-candidates.mjs'))return 'fixture observed';if(file.endsWith('/current-audit-diagnostic.mjs')){fs.writeFileSync('work/nss41/'+args[0]+'-diagnostic-audit-private.json',JSON.stringify({passed:false,error:'fixture source age expired'}));throw Error('fixture audit refusal before checkpoint');}throw Error('Unexpected subprocess '+file);}`);
 const script=path.join(dir,'controller-fixture.mjs');fs.writeFileSync(script,body);const result=spawnSync(process.execPath,[script,'aba'],{cwd:dir,encoding:'utf8',timeout:10000,windowsHide:true});assert.equal(result.error,undefined);
 const events=fs.existsSync(path.join(dir,'events.txt'))?fs.readFileSync(path.join(dir,'events.txt'),'utf8'):'';assert.ok(!events.includes('router-connect'));
 const rounds=fs.readdirSync(path.join(dir,'work/nss41'),{withFileTypes:true}).filter(n=>n.isDirectory()&&n.name.startsWith('real-matched-aba-')).map(n=>n.name);
 if(scenario==='no-application-pair'){assert.equal(result.status,0,result.stderr);assert.equal(rounds.length,0);assert.ok(!events.includes('current-audit'));}
 else{assert.equal(result.status,1);assert.equal(rounds.length,1);const attempt=path.join(dir,'work/nss41',rounds[0]);assert.ok(fs.existsSync(path.join(attempt,'selected-preaudit-private.json')));
  if(scenario==='audit-refusal'){
   for(const [name,digest] of Object.entries(app.manifest))assert.equal(hash(fs.readFileSync(path.join(attempt,'application-preaudit',name))),digest);
   assert.equal(hash(fs.readFileSync(path.join(attempt,'frozen/fixture-source.txt'))),sourceHash);
   const rr=JSON.parse(fs.readFileSync(path.join(attempt,'result.json')));assert.equal(rr.passed,false);assert.equal(rr.matchedForwardingABACompleted,false);assert.ok(rr.errors[0].includes('fixture audit refusal'));assert.ok(events.includes('current-audit'));assert.ok(fs.existsSync(path.join(dir,'work/nss41',rounds[0]+'-before-diagnostic-audit-private.json')));
  }else{assert.ok(!events.includes('current-audit'));assert.ok(!fs.existsSync(path.join(attempt,'source-manifest-preaudit.json')));}
 }
 cases.push({case:scenario,passed:true,configurationMutationCalls:0,exitCode:result.status});
 fs.writeFileSync(path.join(dir,'test-process-private.json'),JSON.stringify({stdout:result.stdout,stderr:result.stderr},null,2));
}
const out={passed:true,checks:cases.length,cases,controllerSha256:hash(actual),scope:'Actual controller ordering through preaudit archive/refusal, with fake application IO and forced audit rejection. No router, game, native gate, or staging writes.',routerWrites:false,fixtureDirectory:path.relative(root,base).replaceAll('\\','/')};fs.writeFileSync(path.join(here,'preaudit-archive-qualified.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out));
