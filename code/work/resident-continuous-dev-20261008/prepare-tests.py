from pathlib import Path
root=Path(__file__).resolve().parent
base=root.parent/'resident-general-dev-i-20261008'
s=(base/'test-subsets.mjs').read_text()
s=s.replace("import{materializeNormal}from'../resident-normal-dev-i-20261008/materialize-normal.mjs';", "import{materializeContinuous as materializeNormal}from'./adapt.mjs';")
for name in ['selection','class-leaf-map','wan-tag-plan','candidate-policy','adapt-plane']:
    s=s.replace("from'./"+name+".mjs'", "from'../resident-general-dev-i-20261008/"+name+".mjs'")
s=s.replace("const root='work/resident-general-dev-i-20261008'", "const root='work/resident-continuous-dev-20261008'")
a="for(const k of ['guardianSourceSha256'"
b="const module=fs.readFileSync(root+'/endpoint-gate/rp_ecm_gate_lab_ct.runtime.ko');input.moduleBytes=module.length;input.moduleSha256=crypto.createHash('sha256').update(module).digest('hex');\n for(const k of ['guardianSourceSha256'"
assert s.count(a)==1;s=s.replace(a,b)
(root/'test-subsets.mjs').write_text(s)
print('Continuous subset size/syntax models prepared')
