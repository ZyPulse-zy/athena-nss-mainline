"""Extend the immutable tuple set, retaining classifier policy and five-WAN QoS."""
from pathlib import Path
import re
w=Path(__file__).resolve().parents[2];old=w/'work/v20-five';root=w/'work/v21-fiveflow'
names=['tcp','udp','tcp2','tcp3','tcp4'];lua="{'tcp','udp','tcp2','tcp3','tcp4'}";js="['tcp','udp','tcp2','tcp3','tcp4']";native="{'tcp','game','tcp2','tcp3','tcp4'}"
for p in old.iterdir():
 if not p.is_file() or p.suffix not in ['.mjs','.lua','.py','.ps1'] or any(x in p.name for x in ['private','failure']) or p.name.startswith(('qualify','analyze','export')):continue
 s=p.read_text(encoding='utf8').replace('work/v20-five','work/v21-fiveflow').replace('work\\/v20-five','work\\/v21-fiveflow').replace('v20-five-','v21-fiveflow-')
 s=re.sub(r"\['tcp',\s*'udp',\s*'tcp2'\]",js,s);s=re.sub(r"\{'tcp',\s*'udp',\s*'tcp2'\}",lua,s);s=s.replace("{'tcp','game','tcp2'}",native)
 if p.name=='session-binding.mjs':s=s.replace('../v19-borrow/session-binding.mjs','../v20-five/session-binding.mjs')
 if p.name=='guardian-plan.mjs':s=s.replace("['tcp','tcp2','udp']","['tcp','tcp2','tcp3','tcp4','udp']").replace('delete compact.selected;','delete compact.selected;delete compact.wanPrerequisites;')
 if p.name=='payload.mjs':
  s=s.replace("const selection=JSON.stringify(input.selected);", "const prerequisites=JSON.stringify(input.wanPrerequisites);assert.ok(!prerequisites.includes(']====]'));const selection=JSON.stringify(input.selected);")
  s=s.replace("return{selected=selected,qos=qos", "local prerequisites=assert(require(\"luci.jsonc\").parse([====['+prerequisites+']====]));return{selected=selected,wanPrerequisites=prerequisites,qos=qos")
 if p.name=='candidate-policy.mjs':
  a=s.index('const a=input.selected.tcp');b=s.index('\n}',a)
  s=s[:a]+"const p=input.wanPrerequisites;assert.equal(p.boot,q.boot);const flows=Object.values(input.selected);assert.deepEqual(Object.keys(input.selected).sort(),['tcp','tcp2','tcp3','tcp4','udp']);assert.equal(p.members.length,5);assert.equal(new Set(flows.map(f=>f.wan)).size,5);\n for(const f of flows){assert.ok(Number.isInteger(f.wan)&&f.wan>=1&&f.wan<=5);assert.equal(f.original.src,'192.168.237.207');assert.equal(f.zone,0);assert.equal((f.mark>>>16)&255,f.wan);assert.equal(f.mark&0x2000,0);assert.ok(Number.isInteger(f.id)&&f.id>0&&f.id<=0xffffffff);const e=p.members.find(e=>e.w===f.wan);assert.ok(e&&e.ip===f.reply.dst&&e.index>0&&e.pid>1&&/^\\d+$/.test(e.start));}\n"+s[b:]
  # Preserve the existing 2048-character typed module-argument bound.
  # The per-command encode limit remains 9000; this is typed plan text, not a transport permission.
 if p.name=='class-leaf-map.mjs':s=s.replace("assert.notEqual(selected.tcp.wan,selected.tcp2.wan);", "assert.equal(new Set(Object.values(selected).map(f=>f.wan)).size,5);")
 if p.name=='wan-tag-plan.mjs':
  s=s.replace("['tcp','udp','tcp2'].includes(d.slot)",js+".includes(d.slot)").replace("['tcp','tcp2','udp']","['tcp','tcp2','tcp3','tcp4','udp']")
  s=s.replace("const slot=name.startsWith('tcp2_')?'tcp2':name.startsWith('tcp_')?'tcp':name.startsWith('udp_')?'udp':null;assert.ok(slot);", "const slot=name.match(/^([a-z0-9]+)_/)?.[1];assert.ok("+js+".includes(slot));")
 if p.name=='classifier.lua':
  s=s.replace("assert(selected.tcp.wan~=selected.tcp2.wan,'Distinct naturally selected WANs required')", "local seen={};for _,f in pairs(selected)do assert(not seen[f.wan],'Distinct naturally selected WANs required');seen[f.wan]=true end")
 if p.name=='wan-scope.lua':s=s.replace('assert(#members>=2 and #members<=3)','assert(#members==5)')
 if p.name=='classified-tags.lua':
  s=s.replace("assert(pair.tcp and pair.udp and pair.tcp2 and pair.tcp2.decision.class=='BULK'and pair.tcp.decision.class=='BULK'and pair.udp.decision.class=='RT'and pair.udp.decision.budgetAdmitted,'Current permanent classifier did not admit exact pair')", "for _,slot in ipairs("+lua+")do local f=assert(pair[slot],'Selected classified flow absent');assert(f.decision.class==(slot=='udp'and'RT'or'BULK')and(slot~='udp'or f.decision.budgetAdmitted),'Current permanent classifier did not admit exact five flows')end")
  s=s.replace('{pair.tcp,pair.udp,pair.tcp2}','{pair.tcp,pair.udp,pair.tcp2,pair.tcp3,pair.tcp4}')
 if p.name=='fast-path.lua':
  before="{'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down','tcp2_post_up','tcp2_post_down'}"
  post="{'tcp_post_up','tcp_post_down','udp_post_up','udp_post_down','tcp2_post_up','tcp2_post_down','tcp3_post_up','tcp3_post_down','tcp4_post_up','tcp4_post_down'}";s=s.replace(before,post)
  s=s.replace("and k.tcp2_permit=='Y'", "and k.tcp2_permit=='Y'and k.tcp3_permit=='Y'and k.tcp4_permit=='Y'")
  s=s.replace('v<=3,','v<=5,').replace("accelerated_count']~=3", "accelerated_count']~=5").replace("connection_count']~=3", "connection_count']~=5")
  s=s.replace('{P.selected.tcp,P.selected.udp,P.selected.tcp2}', '{P.selected.tcp,P.selected.udp,P.selected.tcp2,P.selected.tcp3,P.selected.tcp4}')
  # Complete native table validation and counter audit remain before recording.
  # Store counter-only copies for repeated snapshots; keep tagsAfter as one full readback.
  needle=' local function G(key,I,pending)';assert s.count(needle)==1
  s=s.replace(needle," local function tagProof(raw)return{completeNativeTableValidated=true,counters=counters(raw)}end\n"+needle)
  s=s.replace('R[key]=raw;','R[key]=tagProof(raw);').replace("R[key..'First']=raw", "R[key..'First']=tagProof(raw)")
  s=s.replace('R.startupTags=I();H=counters(R.startupTags);M.tagEpoch(H,H)', 'local startup=I();H=counters(startup);R.startupTags=tagProof(startup);M.tagEpoch(H,H)')
 if p.name=='module-stage-guardian.lua':
  s=s.replace('assert(P.selected==nil);P.selected=assert(bundle.selected);','assert(P.selected==nil and P.wanPrerequisites==nil);P.selected=assert(bundle.selected);P.wanPrerequisites=assert(bundle.wanPrerequisites);')
  a=s.index(' local function parameters()');b=s.index('\n local function undoModule',a)
  s=s[:a]+" local function parameters()local o={};local function get(name)o[name]=read('/sys/module/'..MOD..'/parameters/'..name,8192):gsub('%s+$','')end;for _,name in ipairs({'registered','diagnostic_only','denied','last_decoded_info','frozen_record_sha256','classifier_until_ms','session_until_ms','classifier_sequence','epoch_refresh','renewed_epochs','cpu_barriers','revoke_calls','revoke_found'})do get(name)end;for _,slot in ipairs("+native+")do for _,prefix in ipairs({'eligible','allowed','expiry'})do get(prefix..'_'..slot)end;for _,suffix in ipairs({'state','pinned_state','permit'})do get(slot..'_'..suffix)end end;return o end"+s[b:]
 if p.name=='module-stage.mjs':s=s.replace('work/v16-three/endpoint-gate','work/v21-fiveflow/endpoint-gate').replace('work/v16-three/runtime-elf-comparison.json','work/v21-fiveflow/runtime-elf-comparison.json').replace('work/v16-three/native-source-qualified.json','work/v21-fiveflow/native-source-qualified.json')
 if p.name=='epoch-driver.mjs':
  s=s.replace("[['tcp','tcp'],['udp','game'],['tcp2','tcp2']]", "[['tcp','tcp'],['udp','game'],['tcp2','tcp2'],['tcp3','tcp3'],['tcp4','tcp4']]")
  s=s.replace("assert.equal(classified.decisions[2].class,'BULK');", "assert.equal(classified.decisions[2].class,'BULK');assert.equal(classified.decisions[3].class,'BULK');assert.equal(classified.decisions[4].class,'BULK');")
  a=s.index("assert.ok(fresh.udp.some(");b=s.index(',\'Exact controlled socket pair changed before staging\');',a)
  s=s[:a]+"assert.ok("+js+".every(slot=>(slot==='udp'?fresh.udp:fresh.tcp).some(f=>JSON.stringify(convert(f))===JSON.stringify(selected[slot])))"+s[b:]
 (root/p.name).write_text(s,encoding='utf8')
print('Five-flow controller candidate copied; classifier thresholds/QoS and limits unchanged')
