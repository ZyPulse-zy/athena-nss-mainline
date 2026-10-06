from pathlib import Path
root=Path('work/nss159')
def copy(old,new,replacements=()):
    data=Path(old).read_text(encoding='utf-8')
    for a,b in replacements:
        assert a in data,(old,a)
        data=data.replace(a,b)
    (root/new).write_text(data,encoding='utf-8',newline='\n')
for name in ['receiver.py','server.py','endpoint-firewall-guardian.py','discover-peer.py','probe-peer.py','client-watchdog.ps1']:
    (root/name).write_bytes((Path('work/nss157')/name).read_bytes())
for name in ['close-endpoint.mjs','read-controlled.mjs']:
    copy('work/nss157/'+name,name,[('work/nss157','work/nss159')])
for name in ['declared-baseline.mjs','failed-wan-owner.lua']:
    (root/name).write_bytes((Path('work/nss158')/name).read_bytes())
copy('work/nss158/current-audit-diagnostic.mjs','current-audit-diagnostic.mjs',[('work/nss158','work/nss159')])
copy('work/nss157/start-dallas-v3.mjs','start-dallas.mjs',[
 ('work/nss157','work/nss159'),("'nss157-'","'nss159-'"),
 ("assert.equal(process.argv[2],'upload');assert.ok(process.argv[3]===undefined||process.argv[3]==='class-retry');config.allowPreparationRetry=process.argv[3]==='class-retry';", "assert.equal(process.argv[2],'download');assert.equal(process.argv[3],undefined);"),
 ("config.bulkDirection='upload'","config.bulkDirection='download'"),
 ("root+'/cohort-client-v2.mjs'","root+'/download-client.mjs'"),
 ('owned SSH upload with fixture-only keepalive disabled','owned SSH download with acknowledged sender replacement')])
copy('work/nss158/epoch-driver.mjs','epoch-driver.mjs',[
 ("from './module-stage.mjs'","from '../nss158/module-stage.mjs'"),
 ("observationRoot='work/nss157'","observationRoot='work/nss159'"),
 ('work/nss158/automatic-epoch-','work/nss159/automatic-epoch-'),
 ('work/nss158/current-audit-diagnostic.mjs','work/nss159/current-audit-diagnostic.mjs'),
 ('nss158\\/pilot-aba-','nss159\\/pilot-aba-')])
copy('work/nss158/pilot-supervisor.mjs','pilot-supervisor.mjs',[
 ("import {requireOwnedUpload} from '../nss157/combined-policy.mjs';","import {requireOwnedDownload} from './owned-load-policy.mjs';"),
 ('work/nss158','work/nss159'),('NSS158 finite same-load ABA','NSS159 finite controlled DOWNLOAD ABA'),
 ('work/nss157/start-dallas-v3.mjs','work/nss159/start-dallas.mjs'),
 ("['upload','class-retry']","['download']"),
 ('work/nss157/match-controlled-v2.mjs','work/nss159/match-controlled.mjs'),
 ('work/nss157','work/nss159'),('requireOwnedUpload(','requireOwnedDownload(')])
copy('work/nss158/session-binding.mjs','session-binding.mjs',[
 ("'../nss157/session-binding-live.mjs'","'../nss158/session-binding.mjs'"),
 ('work/nss158/entry-qualified.json','work/nss159/entry-qualified.json')])
print('Prepared NSS159 namespace; native158 reused without byte changes')
