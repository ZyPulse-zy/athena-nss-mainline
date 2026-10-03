"""Verify curated source identity, artifact links, and obvious secret exclusions."""
import hashlib, json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'source-manifest.json').read_text(encoding='utf-8'))
for item in manifest['sources']:
    file=root/item['path']; assert file.is_file(), item['path']
    assert hashlib.sha256(file.read_bytes()).hexdigest()==item['sha256'],item['path']
rules={
 'private-key':r'-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----',
 'github-token':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b',
 'openai-token':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{35,}',
 'credential-url':r'https?://[^\s/]+:[^\s/@]+@',
 'literal-password':r'''(?i)(?:password|passwd|access_token|refresh_token)\s*[:=]\s*["'][^"'\s]{8,}["']''',
}
count=0; links=0
for file in root.rglob('*'):
    if not file.is_file() or '.git' in file.relative_to(root).parts or '.local' in file.relative_to(root).parts: continue
    rel=file.relative_to(root).as_posix()
    assert not re.search(r'(?i)(?:^|/)(?:connect-router[^/]*|.*private.*|.*credential.*|deployment-latest\.json)$',rel), 'Excluded filename: '+rel
    assert file.suffix.lower() not in ('.ko','.o','.key','.pem','.pfx','.clixml','.zip','.gz'),rel
    text=file.read_text(encoding='utf-8'); assert '\ufffd' not in text,rel
    for name,pattern in rules.items():
        if re.search(pattern,text): raise AssertionError('Potential secret ('+name+') in '+rel)
    if file.suffix=='.md':
        for dest in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
            if re.match(r'^https?://',dest): continue
            assert (file.parent/dest.split('#')[0]).resolve().exists(),rel+' -> '+dest
            links+=1
    count+=1
s=json.loads((root/'evidence/nss33-summary.json').read_text())
assert s['realTrial']['passed'] is False and s['realTrial']['rollbackPassed'] is True
assert not s['nssHighLoadCpuBenefitProved'] and not s['cs2JitterLossMissCaptured']
assert s['realTrial']['bulkLeaf']['packets']==s['realTrial']['rtLeaf']['packets']==0
n=json.loads((root/'evidence/nss35-address-recovery.json').read_text())
c=json.loads((root/'evidence/current-runtime.json').read_text())
assert n['checks']==136 and n['classifier']['committed'] and n['automaticRollback']['passed']
assert c['round']=='NSS37' and c['deploymentReference']=='work/nss37/deployment-latest.json'
assert n['protectedAudit']['ecmClosedAndZero'] and not n['safety']['nssGateOrQdiscLoaded']
assert not n['limitations']['productionAddressFailureInjected'] and not n['limitations']['highLoadCpuBenefitProved']
assert not n['limitations']['cs2JitterLossMissCaptured']
x=json.loads((root/'evidence/nss36-mainline.json').read_text())
assert x['checks']==299 and x['controller']['configuration']['configSha256']==n['classifier']['configSha256']
t=x['actualTrial']
assert t['attempted'] and not t['passed'] and not t['matchedForwardingABACompleted'] and t['rollbackPassed']
assert t['probeCount']==44 and t['readyCount']==0 and sum(t['refusalCounts'].values())==44
assert t['physicalLan4QosTreePrepared'] and not t['packetTagRulesInstalled'] and not t['gateModuleLoaded'] and not t['nssPermissionGranted']
assert t['bulkLeaf']['packets']==t['rtLeaf']['packets']==0
assert x['finalState']['previousAuditRejectedStaleSnapshot'] and x['finalState']['subsequentAuditPassed'] and x['finalState']['ecmClosedAndZero']
assert not x['limitations']['nssCpuBenefitProved'] and not x['limitations']['gameJitterLossMissCaptured']
y=json.loads((root/'evidence/nss37-normalizer.json').read_text())
assert y['localChecks']==9113 and y['differential']['checks']==9087 and y['lifecycle']['checks']==26
assert y['classifier']['committed'] and y['classifier']['configSha256']==c['classifierConfigSha256']
assert y['change']['onlyAttributeSearchChanged'] and y['change']['sourceScopePolicyAndDeadlinesUnchanged']
assert hashlib.sha256((root/'code/work/nss35/conntrack-source.lua').read_bytes()).hexdigest()==y['change']['oldSha256']
assert y['change']['newSha256']==y['classifier']['sourceSha256']==y['differential']['sourceSha256']
assert hashlib.sha256((root/'code/deployed-classifier/conntrack-source.lua').read_bytes()).hexdigest()==y['change']['newSha256']
assert y['automaticRollback']['automaticExpiryWithoutControllerRollback'] and y['automaticRollback']['previousNormalizerAndGuardianRestored']
assert len(y['installations'])==2 and all(v['rollbackVerifiedBeforeConfigMutation'] and v['independentOfControlConnection'] for v in y['installations'])
assert sum(len(v['samples']) for v in y['nativeBenchmark']['results'])==16
assert all(v['allOutputsEqual'] and v['cpuReductionPercent']>20 for v in y['nativeBenchmark']['results'])
assert all(v['allHealthy'] and v['samples']==35 and v['ecmClosedAndZero'] for v in y['windows'].values())
assert y['controller']['sourceManifestEntries']==66 and y['controller']['newSyntheticSelectionChecks']==10
assert y['controller']['configuration']['configSha256']==c['classifierConfigSha256']
assert y['finalState']['protectedAudit']['ecmClosedAndZero'] and y['finalState']['sameProducerSincePermanentObservation']
assert not y['actualFastPathTrial']['attempted'] and not y['actualFastPathTrial']['ecmOpened']
assert not y['limitations']['realHighLoadABACompleted'] and not y['limitations']['nssCpuBenefitProved'] and not y['limitations']['gameJitterLossMissCaptured']
print(json.dumps({'passed':True,'filesChecked':count,'sourceHashesChecked':len(manifest['sources']),'markdownLinksChecked':links,'obviousSecretChecksPassed':True,'scope':'Curated allowlist plus pattern checks; not a claim of comprehensive secret detection.'}))
