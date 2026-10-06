"""Reuse descriptive lifecycle metrics with server-confirmed upload bytes."""
from pathlib import Path
r=Path(__file__).resolve().parent;w=r.parents[1]
s=(w/'work/nss150/reporting/analyze.py').read_text(encoding='utf-8')
a="r=read(p/'last-record-private.json');result=read(p/'result.json')\nassert result['passed'] and result['automaticLifecycleEpochCompleted'] and not result['matchedForwardingABACompleted']"
b="record=p/'crash-last-record-private.json'\nif record.exists():\n    r=read(record);result=read(p.parent/'run-v4/independent-crash-result.json')\n    assert result['passed'] and result['originalControllerKilledDuringEcm2']\nelse:\n    r=read(p/'last-record-private.json');result=read(p/'result.json')\n    assert result['passed'] and result['automaticLifecycleEpochCompleted'] and not result['matchedForwardingABACompleted']\nassert r['automaticLifecycleEpochCompleted'] and r['firmwareZeroAfterRetirement'] and not r['abaCompleted']"
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("'clientTcpReceivedMbps'", "'serverConfirmedTcpUploadMbps'").replace("metrics['clientTcpReceivedMbps']", "metrics['serverConfirmedTcpUploadMbps']").replace("'downloadMbps'", "'uploadMbps'")
s=s.replace("'phase':'NSS lifecycle'", "'phase':'NSS upload lifecycle'")
s=s.replace("'selectedWan':read", "'direction':'upload',\n 'tcpMetric':'server-confirmed received bytes',\n 'selectedWan':read")
p=r/'analyze.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='')
print('Upload lifecycle analysis prepared; CPU causal comparison remains null.')
