from pathlib import Path
r=Path('work/nss122');r.mkdir(exist_ok=True)
s=Path('work/nss68/wait-ready-candidate.mjs').read_text(encoding='utf-8')
s=s.replace("from './deployment-binding.mjs'", "from '../nss68/deployment-binding.mjs'")
s=s.replace("const library=fs.readFileSync('work/nss49/publication-wait.lua','utf8');", "const library=fs.readFileSync('work/nss49/publication-wait.lua','utf8');const atomicReader=fs.readFileSync('work/nss122/atomic-hint-read.lua','utf8');")
old="local function stable(p,l)local a=assert(fs.lstat(p));assert(a.type=='reg'and a.uid==0 and a.gid==0 and a.nlink==1);local s=read(p,l);local b=assert(fs.lstat(p));assert(a.dev==b.dev and a.ino==b.ino,'Publication changed during scheduling read');return s,b end"
new="local Atomic=assert(loadstring([====[${atomicReader}]====]))();local raceReads={};local function stable(p,l)return Atomic.stable(fs,read,p,l,function(x)raceReads[#raceReads+1]=x end)end"
assert s.count(old)==1;s=s.replace(old,new).replace('lastIoPhase=ioPhase,','lastIoPhase=ioPhase,discardedAtomicReads=raceReads,').replace("'work/nss68/'+label","'work/nss122/'+label").replace("fs.readFileSync('work/nss68/wait-ready-candidate.mjs')","fs.readFileSync('work/nss122/wait-ready-candidate.mjs')")
(r/'wait-ready-candidate.mjs').write_text(s,encoding='utf-8')
s=Path('work/nss68/wait-publication-metadata.mjs').read_text(encoding='utf-8').replace("'work/nss68/'+label","'work/nss122/'+label")
(r/'wait-publication-metadata.mjs').write_text(s,encoding='utf-8')
