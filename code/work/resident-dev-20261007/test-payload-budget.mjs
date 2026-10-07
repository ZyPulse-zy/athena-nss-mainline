import fs from 'node:fs';
import assert from 'node:assert/strict';
import {packLua} from '../nss149/pack-lua.mjs';
import {patchResidentWindow} from './resident-window.mjs';
import {executeLua,luaLiteral} from './lua-local.mjs';
const root='work/resident-dev-20261007';
const previous='work/resident-rc1-run-20261007161531-ae2bb91a';
const oldFast=fs.readFileSync(previous+'/fast-path.lua','utf8');
const nextFast=patchResidentWindow(fs.readFileSync('work/v20-five/fast-path.lua','utf8'));
const plan=JSON.parse(fs.readFileSync(previous+'/session-20261007161633-c4b2a439/stage-plan-private.json'));
const packedOldBytes=Buffer.byteLength(packLua(oldFast)),packedNextBytes=Buffer.byteLength(packLua(nextFast));
const frozenInputBundleBytes=plan.qosCodeBytes+packedNextBytes-packedOldBytes;
assert.ok(Number.isInteger(plan.qosCodeBytes)&&plan.qosCodeBytes>0);
assert.ok(frozenInputBundleBytes>0&&frozenInputBundleBytes<=73728,'Original complete bundle limit');
const raw=executeLua('assert(loadstring('+luaLiteral(nextFast)+'));assert(loadstring('+luaLiteral(packLua(nextFast))+'));print("2")\n','payload-budget');
assert.equal(raw.code,0,raw.stderr);assert.equal(raw.stdout.trim(),'2');
const out={passed:true,checks:3,actualLua51Syntax:true,routerAccess:false,
 previousActualBundleBytes:plan.qosCodeBytes,packedFastDeltaBytes:packedNextBytes-packedOldBytes,
 frozenInputBundleBytes,maximumBundleBytes:73728,newActualInputMustStillPassBeforeWrite:true,rawDirectory:raw.directory};
fs.writeFileSync(raw.directory+'/summary.json',JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(out));
