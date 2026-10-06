import fs from 'node:fs';import assert from 'node:assert/strict';
const root='work/nss156',run=root+'/run4',load=JSON.parse(fs.readFileSync(root+'/load-latest-private.json')),ref=JSON.parse(fs.readFileSync(run+'/load-reference-private.json'));assert.equal(load.dir,ref.dir);
const cfg=JSON.parse(fs.readFileSync(load.dir+'/client-config-private.json')),s=JSON.parse(fs.readFileSync(load.dir+'/status-private.json'));
assert.equal(s.session,cfg.session);assert.equal(s.pid,load.clientPid);
assert.ok(fs.readFileSync(root+'/epoch-driver-v4.mjs','utf8').includes("'work/nss156/run1/continuity-private.json'"));assert.ok(!fs.existsSync(run+'/first-case-private.json'));
fs.writeFileSync(run+'/prewrite-namespace-detection.json',JSON.stringify({observed:true,generatorLeftOldDirectoryAllowlist:true,stageNotStarted:true,stoppedOnlyOwnedFixture:true,qualifiedSyntaxChecksDidNotCoverWholeFactory:true,frozenSourceUnchanged:true},null,2)+'\n',{flag:'wx'});
fs.writeFileSync(load.dir+'/control.json.new',JSON.stringify({session:cfg.session,stop:true}));fs.renameSync(load.dir+'/control.json.new',load.dir+'/control.json');console.log(JSON.stringify({ownLoadStopRequested:true,oldDirectoryAllowlistDetected:true,routerStageStarted:false}));
