from pathlib import Path
import json
r=Path(__file__).resolve().parent;s=(r/'calibrate-clock.mjs').read_text(encoding='utf-8');before='work\\/nss155\\/';assert s.count(before)==1
s=s.replace(before,'work\\/nss156\\/');p=r/'calibrate-clock-v2.mjs';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
out={'failure':'Original calibration helper retained old nss155 input allowlist','refusedBeforeRouterConnect':True,'oldSourceRetained':True,'onlyExactNamespaceChanged':True,'metricAnalysisNotRunBeforeRepair':True};p=r/'calibration-namespace-failure.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print('Exact calibration namespace repaired in new file; initial refusal/source retained.')
