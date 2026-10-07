from pathlib import Path
r=Path('work/v40-five-sim');s=(r/'capture-client-closure.ps1').read_bytes().decode();a="@('work/v40-five-sim')";assert s.count(a)==1;s=s.replace(a,"@('work/v39-five-sim','work/v40-five-sim')")
with (r/'capture-all-owned-closure.ps1').open('xb') as f:f.write(s.encode())
print('Exact original client and guard closures for both fresh scopes will be checked.')
