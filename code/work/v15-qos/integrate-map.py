from pathlib import Path
root=Path(__file__).resolve().parent;w=root.parent.parent
def edit(name,changes):
 p=root/name;s=p.read_text(encoding='utf-8')
 for a,b,n in changes:
  assert s.count(a)==n,(name,a,s.count(a),n);s=s.replace(a,b)
 p.write_text(s,encoding='utf-8',newline='')
edit('class-leaf-map.mjs',[("import{canonicalSelection}","import{wanTags}from'./wan-tag-plan.mjs';import{canonicalSelection}",1),
 ('epochUntil=Math.min(epochUntil,f.validUntilUptime);decisions.push','const native=wanTags(wanted.wan,d.class);epochUntil=Math.min(epochUntil,f.validUntilUptime);decisions.push',1),
 ('downTag:tag.down,upTag:tag.up','downTag:native.down,upTag:native.up',1)])
edit('epoch-driver.mjs',[("const tagPlan={table:template.expected.nftables[0].table.name,owner,mode:'rt',expected:template.expected};","const tagPlan={table:template.expected.nftables[0].table.name,owner,mode:'rt',expected:template.expected,wanLeafAssignments:template.wanLeafAssignments};",1)])
edit('parse-ecm.mjs',[("const f=selected[slot],up=slot==='tcp'?0x8e050000:0x8e060000;","const f=selected[slot],minor=f.wan*16+(slot==='tcp'?5:6),up=(0x8e00+minor)*65536;tag=(0x8f00+minor)*65536;",1),
 ("for(const[slot,tag]of","for(let[slot,tag]of",1)])
normalizer=(w/'work/nss149/tag-normalizer.lua').read_text(encoding='utf-8')
marker="local function normalized(raw)";assert normalizer.count(marker)==1
derived="""local approved={}
for _,slot in ipairs({'tcp','udp'})do local d=assert(PLAN.wanLeafAssignments[slot]);local low=slot=='tcp'and 5 or 6;assert(d.wan%1==0 and d.wan>=1 and d.wan<=5 and d.class==(slot=='tcp'and'BULK'or'RT'));assert(d.upTag==(0x8e00+d.wan*16+low)*65536 and d.downTag==(0x8f00+d.wan*16+low)*65536);approved[slot..'_writer_up']=d.upTag;approved[slot..'_writer_down']=d.downTag;aliases.priority[string.format('%x:0',d.upTag/65536)]=d.upTag;aliases.priority[string.format('%x:0',d.downTag/65536)]=d.downTag end
assert(PLAN.wanLeafAssignments.tcp.wan~=PLAN.wanLeafAssignments.udp.wan)
"""
normalizer=normalizer.replace(marker,derived+marker)
old="local approved={tcp_writer_up=0x8e050000,udp_writer_up=0x8e060000,tcp_writer_down=0x8f050000,udp_writer_down=0x8f060000};";assert normalizer.count(old)==1;normalizer=normalizer.replace(old,'')
with (root/'tag-normalizer.lua').open('x',encoding='utf-8',newline='') as f:f.write(normalizer)
edit('candidate-policy.mjs',[("assert.equal(a.protocol,6);assert.equal(b.protocol,17);","assert.equal(a.protocol,6);assert.equal(b.protocol,17);for(const[slot,f]of[['tcp',a],['udp',b]]){const m=input.tagPlan.wanLeafAssignments[slot],low=slot==='tcp'?5:6;assert.equal(m.wan,f.wan);assert.equal(m.class,slot==='tcp'?'BULK':'RT');assert.equal(m.upTag,(0x8e00+f.wan*16+low)*65536);assert.equal(m.downTag,(0x8f00+f.wan*16+low)*65536);}",1),
 ("for(const k of['owner','table','mode'])assert.equal(after.tagPlan[k],before.tagPlan[k]);","for(const k of['owner','table','mode'])assert.equal(after.tagPlan[k],before.tagPlan[k]);assert.deepEqual(after.tagPlan.wanLeafAssignments,before.tagPlan.wanLeafAssignments);",1)])
print('WAN-specific mapping integrated; not production permission')
