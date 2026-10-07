import fs from 'node:fs';import assert from 'node:assert/strict';import {root} from './build-classifier.mjs';import {connectRouter} from '../nss20/connect-router.mjs';import {encode,receipt} from '../nss11/v7-observe-repair/observe2/transport.mjs';
const code=String.raw`local j=require('luci.jsonc');local fs=require('nixio.fs');local n=require('nixio')
local function read(p)local f=assert(io.open(p));local s=f:read(4194305);f:close();assert(#s<=4194304);return s end
local rows={};for i=1,4 do
 local now=tonumber(read('/proc/uptime'):match('^[%d.]+'));local row={at=now}
 for _,name in ipairs({'classification','snapshot','guardian'})do local p='/tmp/router-project-game-classifier/'..name..'.json';local a=j.parse(read(p));local st=fs.lstat(p);row[name]={ino=st.ino,size=st.size,at=a.atUptime,status=a.status,healthy=a.healthy,dataHealthy=a.dataHealthy,pid=a.pid,sourceAge=a.snapshot and now-a.snapshot.provenance.startedAtUptime,sequence=a.snapshot and a.snapshot.provenance.sequence}end
 rows[#rows+1]=row;if i<4 then n.nanosleep(1)end
end;print(j.stringify({readonly=true,rows=rows}))`;
const c=await connectRouter();try{const e=encode("lua - <<'RC_HEALTH'\n"+code+'\nRC_HEALTH\n'),raw=receipt(await c.run(e.command),e);const file=root+'/health-read-'+Date.now()+'-private.json';fs.writeFileSync(file,JSON.stringify(raw,null,2)+'\n',{flag:'wx'});assert.equal(raw.code,0,raw.stderr);console.log(raw.stdout.trim());}finally{c.close();}
