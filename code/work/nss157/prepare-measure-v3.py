from pathlib import Path
r=Path(__file__).resolve().parent;s=(r/'measure-historical-v2.mjs').read_text(encoding='utf-8')
s=s.replace('input.tagPlan=template;',"input.tagPlan={table:template.expected.nftables[0].table.name,owner:input.tagPlan.owner,mode:'rt',expected:template.expected};")
s=s.replace('historical-payload-v2-private.lua','historical-payload-v3-private.lua').replace('measure-historical-v2.json','measure-historical-v3.json').replace('originalV1IncompleteInputFailureRetained:true','originalV1IncompleteInputFailureRetained:true,v2NonRuntimeTemplateFailureRetained:true')
p=r/'measure-historical-v3.mjs';assert not p.exists();p.write_text(s,encoding='utf-8',newline='');print('Measure the exact runtime tag-plan schema; original v1/v2 failed inputs remain.')
