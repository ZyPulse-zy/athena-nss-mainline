from pathlib import Path
import json
r=Path(__file__).resolve().parent
s=(r/'export.py').read_text(encoding='utf-8')
a="cases=[w/v['output'] for v in history['experiments']];assert len(cases)==2"
z="driver=read(r/'run-v5/driver-private.json');actual_trials=[json.loads(v['stdout']) for v in driver if v['file']=='work/nss150/controlled-session-v5.mjs'];assert len(actual_trials)==2 and all(v['passed'] for v in actual_trials);assert history['experiments']==[]\ncases=[w/v['output'] for v in actual_trials]"
assert s.count(a)==1;s=s.replace(a,z)
a="'work/nss150/reporting/export.py','work/nss150/reporting/verify-published.py']"
z="'work/nss150/reporting/export.py','work/nss150/reporting/export-v2.py','work/nss150/reporting/prepare-export-v2.py','work/nss150/reporting/verify-published.py']"
assert s.count(a)==1;s=s.replace(a,z)
a="'failuresPreserved':len(failures),"
z="'oldHistoryExperimentIndexEmptyPreserved':True,'actualTrialReferencesRecoveredFromExactDriverReceipts':True,'reportExportV1FailedBeforeRepositoryWrites':True,'failuresPreserved':len(failures),"
assert s.count(a)==1;s=s.replace(a,z)
with (r/'export-v2.py').open('x',encoding='utf-8') as f:f.write(s)
failure={'passed':False,'originalSourceRetained':True,'reason':'History recorder selected the old unversioned controller filename, so its experiment reference list was empty even though both fully validated epochs and the exact driver receipts are present',
 'bothHardwareEpochResultsPreserved':True,'firstExporterStoppedBeforeRepositoryWrites':True,'hardwareOrOperationalSourceChanged':False,
 'correction':'Build reporting references from the two exact versioned driver receipts; keep the empty old list and original source, no experiment rerun'}
(r/'export-v1-failure.json').write_text(json.dumps(failure,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'prepared':True,'originalExporterKept':True,'noHardwareRerun':True,'repositoryWrites':False}))
