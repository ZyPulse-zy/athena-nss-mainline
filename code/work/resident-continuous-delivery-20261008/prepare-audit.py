from pathlib import Path
w=Path(__file__).resolve().parents[2]
text=(w/'work/resident-delivery-audit-dev-i-20261008.py').read_text(encoding='utf-8')
def once(a,b):
 global text
 assert text.count(a)==1,a
 text=text.replace(a,b)
once("base = 'a667b0af4735d0ddd6d3836912a9747e279f9810'","base = '78c10db6f8220d1925081bd5252ab2f021b31900'")
once('w = Path(__file__).resolve().parents[1]','w = Path(__file__).resolve().parents[2]')
text=text.replace('evidence/resident-independent-admission.json','evidence/resident-continuous.json')
once('assert n == 6178 and','assert n == 6257 and')
once("assert len(fresh) == 79 and len(manifest['sources']) == 6257","assert fresh and len(manifest['sources']) == n + len(fresh)")
once("evidence['actualIntegration']['nssSeconds'] == 90","evidence['actualIntegration']['nssSeconds'] >= 190")
once("evidence['actualIntegration']['allSamplesEcm1']","evidence['actualIntegration']['retainedSamplesEcm1']")
once("'evidence/resident-continuous.json']","'evidence/resident-continuous.json', 'docs/RESIDENT_CONTINUOUS.md',\n        'tools/check_resident_continuous.py', 'tools/check_repository.py']")
once('assert len(allowed) == 90','assert len(allowed) == len(fixed) + len(fresh)')
text=text.replace('completed independent-admission milestone','completed continuous-qualified-residency milestone')
text=text.replace("'resident-publication-'","'resident-continuous-publication-'")
out=Path(__file__).parent/'delivery-audit.py'
with out.open('x',encoding='utf-8',newline='') as f:f.write(text)
compile(text,str(out),'exec')
print('Prepared continuous milestone publication checks; no Git changes or hardware access')
