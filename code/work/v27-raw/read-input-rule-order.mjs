import fs from'node:fs';import assert from'node:assert/strict';import{persistentSsh}from'./persistent-ssh.mjs';
const code=`import json,subprocess
n=json.loads(subprocess.check_output(['nft','-j','list','chain','inet','sub2api','input'],text=True))
out=[]
for x in n['nftables']:
 if 'rule' not in x:continue
 r=x['rule'];e=r['expr'];out.append({'index':len(out),'statementKeys':[list(y) for y in e],'unconditionalTerminalDeny':any('drop' in y or 'reject' in y for y in e) and not any('match' in y or 'jump' in y for y in e),'sourceAddressFiltered':any(y.get('match',{}).get('left',{}).get('payload',{}).get('field')=='saddr' for y in e),'tcpOnly':any(y.get('match',{}).get('left',{}).get('meta',{}).get('key')=='l4proto' and y['match'].get('right')=='tcp' for y in e),'terminalDeny':any('drop' in y or 'reject' in y for y in e)})
print(json.dumps({'readonly':True,'rules':out}))
`;
const c=persistentSsh();try{const r=await c.exec('python3 -B -E -s -u -',code,{milliseconds:12000});fs.writeFileSync('work/v27-raw/input-rule-order-raw-private.json',JSON.stringify(r,null,2)+'\n',{flag:'wx'});assert.equal(r.code,0,r.stderr);const v=JSON.parse(r.stdout);fs.writeFileSync('work/v27-raw/input-rule-order-summary.json',JSON.stringify(v,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(v));}finally{c.close()}
