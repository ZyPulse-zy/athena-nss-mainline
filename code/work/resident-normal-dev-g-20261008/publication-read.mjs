import assert from 'node:assert/strict';
export const originalRead=` local function stable(path,cap)
  local a=assert(fs.lstat(path));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1)
  local body=read(path,cap);local b=assert(fs.lstat(path))
  assert(a.dev==b.dev and a.ino==b.ino,'Classifier publication changed during read');return body
 end`;
export const boundedRead=` local function stable(path,cap)
  local due=math.min(now()+0.05,(record.deadline or 0)-6)
  for attempt=1,2 do
   local a=assert(fs.lstat(path));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1)
   local body=read(path,cap);local b=assert(fs.lstat(path))
   if a.dev==b.dev and a.ino==b.ino then assert(attempt==1 or now()<due,'Classifier publication reread time exhausted');return body end
   assert(attempt==1 and now()<due and(path==ram..'/classification.json'or path==ram..'/guardian.json'or path==ram..'/snapshot.json'),'Classifier publication changed during read')
  end
 end`;
// Atomic rename can replace the path while an open file returns complete old
// bytes. Only these publication channels get one immediate fresh read, with a
// 50 ms cap and no sleep/cache. Config/owner and all provenance, CT, class and
// lease checks retain their exact original behavior.
export function patchPublicationRead(source){
 const eol=source.includes('\r\n')?'\r\n':'\n';
 const original=originalRead.replaceAll('\n',eol),candidate=boundedRead.replaceAll('\n',eol);
 assert.equal(source.split(original).length,2,'Exact original publication reader required');
 const next=source.replace(original,candidate);
 assert.equal(next.replace(candidate,original),source,'Only publication helper may change');
 return next;
}
