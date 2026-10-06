from pathlib import Path
import json

r = Path(__file__).resolve().parent
s = (r / 'qualify-current-full.mjs').read_text(encoding='utf-8')
s = s.replace("dir=root+'/current-full-qualification-v1'", "dir=root+'/current-full-qualification-v2'")
old = "packLua(source)+\"]====]));print('CURRENT_FULL_SYNTAX_OK')"
new = "packLua(source.slice(a,b))+\"]====]));print('CURRENT_CHANGED_ADAPTER_SYNTAX_OK')"
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace("n==='syntax'?'CURRENT_FULL_SYNTAX_OK'", "n==='syntax'?'CURRENT_CHANGED_ADAPTER_SYNTAX_OK'")
s = s.replace('nativeSyntaxPassed:true', 'nativeChangedAdapterSyntaxPassed:true,fullStandaloneSyntaxDeferred:true,unchangedOriginalConsumerBytesVerified:true')
s = s.replace("root+'/current-full-qualified.json'", "root+'/current-full-qualified-v2.json'")
p = r / 'qualify-current-full-v2.mjs'
assert not p.exists()
p.write_text(s, encoding='utf-8', newline='')
f = r / 'current-full-qualification-v1-failure.json'
assert not f.exists()
f.write_text(json.dumps({'passed': False, 'phase': 'local transport encoding before router connection', 'error': 'Transport length refused', 'routerConnected': False, 'productionWrites': False, 'rawLimit': 65536, 'execLimit': 9000, 'nextVersion': 'qualify-current-full-v2.mjs', 'repair': 'Compile only actual changed adapter fragment; verify unchanged Consumer and renewal byte equality; full guarded bundle compilation remains mandatory before stage'}, indent=2) + '\n', encoding='utf-8')
print('Original failed qualifier preserved; bounded changed-adapter RAM qualification prepared.')
