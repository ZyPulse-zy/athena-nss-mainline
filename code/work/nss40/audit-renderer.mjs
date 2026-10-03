import assert from 'node:assert/strict';
export function render(original){
let body=original;
const replace=(a,b)=>{assert.equal(body.split(a).length,2);body=body.replace(a,b);};
replace("local J=assert(j.parse(read('/tmp/router-project-game-classifier/journal.json',4194304)))","trace('hashes-complete');local J=assert(j.parse(read('/tmp/router-project-game-classifier/journal.json',4194304)));trace('journal-parsed')");
replace("local s=assert(j.parse(read('/tmp/router-project-game-classifier/snapshot.json',4194304)))","trace('selectors-complete');local s=assert(j.parse(read('/tmp/router-project-game-classifier/snapshot.json',4194304)));trace('snapshot-parsed')");
replace("assert(now-s.atUptime<9 and now-s.snapshot.provenance.startedAtUptime<6)","diagnostic.freshness={checkedAt=now,publicationAge=now-s.atUptime,sourceAge=now-s.snapshot.provenance.startedAtUptime,sequence=s.snapshot.provenance.sequence,publishedAt=s.atUptime,queryStarted=s.snapshot.provenance.startedAtUptime};trace('freshness-checked');assert(now-s.atUptime<9 and now-s.snapshot.provenance.startedAtUptime<6)");
replace("print(j.stringify(own.jsonProject(out)))","return own.jsonProject(out)");
const code=String.raw`local json=require('luci.jsonc');local diagnostic={events={}}
local function clock()local f=assert(io.open('/proc/uptime'));local s=f:read(128);f:close();return tonumber(s:match('^[%d.]+'))end
local function trace(name)diagnostic.events[#diagnostic.events+1]={name=name,at=clock()}end
trace('locked-audit-start');local result;local ok,err=xpcall(function()result=(function()
${body}
end)()end,debug.traceback);trace('locked-audit-end');print(json.stringify({passed=ok,error=not ok and tostring(err)or nil,diagnostic=diagnostic,result=result,routerConfigurationWrites=false,originalAssertionsRetained=true}))`;
return code;
}
