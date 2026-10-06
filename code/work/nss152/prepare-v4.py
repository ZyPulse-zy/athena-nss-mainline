"""Ignore audit files while finding the one newly created experiment directory."""
from pathlib import Path
r=Path(__file__).resolve().parent
def put(n,s):
    p=r/n;assert not p.exists(),n;p.write_text(s,encoding='utf-8',newline='')
for n in ['epoch-session','current-audit-diagnostic','crash-controller']:
    s=(r/(n+'-v3.mjs')).read_text(encoding='utf-8').replace('./session-binding-v3.mjs','./session-binding-v4.mjs').replace('work/nss152/run-v3/continuity-private.json','work/nss152/run-v4/continuity-private.json')
    if n=='epoch-session':s=s.replace('work/nss152/current-audit-diagnostic-v3.mjs','work/nss152/current-audit-diagnostic-v4.mjs')
    if n=='crash-controller':
        for a,b in [("out=root+'/run-v3'","out=root+'/run-v4'"),('frozen-qualified-inputs-v3','frozen-qualified-inputs-v4'),('entry-source-manifest-v3.json','entry-source-manifest-v4.json'),("root+'/epoch-session-v3.mjs'","root+'/epoch-session-v4.mjs'"),("root+'/current-audit-diagnostic-v3.mjs'","root+'/current-audit-diagnostic-v4.mjs'")]:s=s.replace(a,b)
        s=s.replace("events=[];let started=false,child,ctx,c,killed=false;","events=[];let started=false,child,ctx,c,killed=false,childStdout='',childStderr='';")
        s=s.replace("filter(n=>n.startsWith('automatic-epoch-'))", "filter(n=>n.startsWith('automatic-epoch-')&&fs.statSync(root+'/'+n).isDirectory())")
        s=s.replace("filter(n=>n.startsWith('automatic-epoch-')&&!existing.has(n))", "filter(n=>n.startsWith('automatic-epoch-')&&!existing.has(n)&&fs.statSync(root+'/'+n).isDirectory())")
        s=s.replace("let stdout='',stderr='';child.stdout.on('data',v=>stdout+=v);child.stderr.on('data',v=>stderr+=v);", "child.stdout.on('data',v=>childStdout+=v);child.stderr.on('data',v=>childStderr+=v);")
        s=s.replace('at:new Date().toISOString(),stdout,stderr}', 'at:new Date().toISOString(),stdout:childStdout,stderr:childStderr}')
        s=s.replace("const exit=await closed;assert.notEqual(exit,0);", "const exit=await closed;assert.notEqual(exit,0);assert.ok(!fs.existsSync(caseDir+'/result.json'),'Killed controller unexpectedly completed its normal cleanup');")
        s=s.replace("{code:rc,normalControllerAllowedToRestore:true}", "{code:rc,normalControllerAllowedToRestore:true,stdout:childStdout,stderr:childStderr}")
    put(n+'-v4.mjs',s)
print('Directory-only experiment discovery prepared; first runtime refusal retained.')
