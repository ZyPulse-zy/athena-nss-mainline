// Workspace import/source graph plus explicitly reviewed dynamic dependencies.
// OS libraries and encrypted login data remain outside this source graph.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export const entrypoints=['real-session.mjs','current-audit-diagnostic.mjs','record-candidates.mjs','read-real-candidates.mjs','inspect-classifier.mjs','final-closure.mjs'].map(n=>'work/nss46/'+n);
export function collectDependencyClosure(workspace,roots=entrypoints){
 const result=spawnSync(process.execPath,['--experimental-vm-modules',path.resolve(workspace,'work/nss46/parse-dependency-graph.mjs')],{input:JSON.stringify({workspace:path.resolve(workspace),roots}),encoding:'utf8',windowsHide:true,timeout:10000});assert.equal(result.status,0,result.stderr);return JSON.parse(result.stdout);
}
export function externalTransportBinding(){
 const file='C:/Users/lishu/Documents/Codex/2026-09-11/ax6600-re-cs-02-jdcos-4/work/router-direct-secure.mjs';assert.ok(fs.statSync(file).isFile());
 return{alias:'previously-authorized-router-transport-source',path:file,sha256:hash(file),hashOnly:true,sourceCopied:false,credentialDataIncluded:false};
}
