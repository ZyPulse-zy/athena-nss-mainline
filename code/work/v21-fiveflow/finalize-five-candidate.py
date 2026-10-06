"""Bind the actual new module and preserve the compact guard map through the owner."""
from pathlib import Path
r=Path(__file__).resolve().parent
def edit(name,old,new):
 p=r/name;s=p.read_text();assert s.count(old)==1,(name,old);p.write_text(s.replace(old,new),encoding='utf8')
edit('module-stage-guardian.lua',"P.moduleBytes==44616 and P.moduleSha256=='d53f5cc076f38edabbbd576b19a2fb1befed3e1acc1cb4ae7703c0e0efab12a2'", "P.moduleBytes==55872 and P.moduleSha256=='574ffbecdf3165508f8b2798acee41207431e5997d5268e2c3065dcec1ceb7d4'")
edit('module-stage-guardian.lua',"P.qosStaged and P.selected==nil", "P.qosStaged and P.selected==nil and P.wanPrerequisites==nil")
edit('epoch-driver.mjs',"wanLeafAssignments:template.wanLeafAssignments};", "wanLeafAssignments:template.wanLeafAssignments,guardedCounters:template.guardedCounters};")
edit('epoch-driver.mjs',"p.name==='B'?3:0", "p.name==='B'?5:0")
edit('epoch-driver.mjs',"twoTcpBulkOneUdpRt:true", "fourTcpBulkOneUdpRt:true")
edit('model-five.mjs',"wanLeafAssignments:t.wanLeafAssignments};", "wanLeafAssignments:t.wanLeafAssignments,guardedCounters:t.guardedCounters};")
edit('qos-physical.lua','only three exact kernel-pinned flows','only five exact kernel-pinned flows')
edit('wan-scope.lua','Two immutable natural WAN identities','Five immutable natural WAN identities')
edit('owned-load-policy.mjs','assert.equal(status.maximumPacerCreditBytes,65536);','assert.equal(status.maximumPacerCreditBytes,65536);assert.equal(status.maximumCombinedPacerCreditBytes,65536);')
print('Actual five-slot runtime bound; exact factored guard map retained')
