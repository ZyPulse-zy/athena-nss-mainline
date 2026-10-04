// New directory; do not alter the NSS54 frozen entry or failed receipts.
import fs from'node:fs';import assert from'node:assert/strict';
assert.ok(!fs.existsSync('work/nss55'));fs.mkdirSync('work/nss55');
for(const name of['baseline-publication-join.lua','wait-ready-joined.mjs','test-publication-join.mjs','qualify-entry.mjs','session-binding.mjs','current-audit-diagnostic.mjs','cleanup-audit.mjs','clock-anchor.mjs']){
 let s=fs.readFileSync('work/nss54/'+name,'utf8').replaceAll('nss54','nss55');
 if(name==='baseline-publication-join.lua')s=s.replace("local current=read();local at=clock();local ok,reason=M.ready(expected,current,at)","local current=read();local at=clock();local ok,reason=false,'publication-replaced';if current then ok,reason=M.ready(expected,current,at)end").replace("sequence=current.sequence,sourceAge=at-current.queryStart,publicationAge=at-current.published","sequence=current and current.sequence,sourceAge=current and at-current.queryStart,publicationAge=current and at-current.published");
 if(name==='wait-ready-joined.mjs'){
  const a="local function stable(p)local a=assert(fs.lstat(p));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1);local raw=read(p,4194304);local b=assert(fs.lstat(p));assert(a.dev==b.dev and a.ino==b.ino,'Publication replaced during join read');return assert(j.parse(raw))end";
  assert.equal(s.split(a).length,2);
  s=s.replace(a,"local function stable(p)local f=assert(n.open(p,'r'));local a=assert(f:stat());assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1);local parts={};local bytes=0;while true do local x=assert(f:read(math.min(65536,4194305-bytes)));if #x==0 then break end;bytes=bytes+#x;assert(bytes<=4194304);parts[#parts+1]=x end;local z=assert(f:stat());for _,k in ipairs({'dev','ino','type','uid','gid','modedec','size'})do assert(z[k]==a[k],'Held publication changed in place')end;assert(f:close());local b=assert(fs.lstat(p));if a.dev~=b.dev or a.ino~=b.ino then return nil end;assert(b.type=='reg'and b.uid==0 and b.gid==0 and b.nlink==1 and b.size==a.size);return assert(j.parse(table.concat(parts)))end");
  s=s.replace("local C=stable('/tmp/router-project-game-classifier/classification.json');assert", "local C=assert(stable('/tmp/router-project-game-classifier/classification.json'),'Classification changed before join identity');assert");
  s=s.replace("local F=stable('/tmp/router-project-game-classifier/snapshot.json');assert", "local F=stable('/tmp/router-project-game-classifier/snapshot.json');if not F then return nil end;assert");
 }
 if(name==='test-publication-join.mjs')s=s.replace('return count<3 and old or F()','if count==1 then return nil end;return count==2 and old or F()').replace('check(r.passed and count==3',"check(r.rows[1].reason=='publication-replaced');check(r.passed and count==3").replace('r.checks,13','r.checks,14');
 if(name==='qualify-entry.mjs')s=s.replace('tests.checks,13','tests.checks,14').replace('pureNativeLuaChecks:13','pureNativeLuaChecks:14');
 fs.writeFileSync('work/nss55/'+name,s,{flag:'wx'});
}
console.log('NSS55 narrow held-file revision prepared; NSS54 untouched');
