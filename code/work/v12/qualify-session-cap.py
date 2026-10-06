"""Execute the actual init lease checks at the old and new time boundaries."""
from pathlib import Path
import hashlib, json, subprocess

root = Path(__file__).resolve().parent
candidate = root/'endpoint-gate/rp_ecm_gate_lab_ct.c'
original = root.parent/'nss27/endpoint-gate/rp_ecm_gate_lab_ct.c'
results=[]
for label,path,maximum in [('historical',original,30000),('candidate',candidate,120000)]:
    text=path.read_text(encoding='utf-8')
    start=text.index('static int __init init_gate(void)')
    text=text[start:text.index(' if (!register_gate',start)]
    start=text.index(' if (!diagnostic_only)')
    checks=text[start:]
    prefix='''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <errno.h>
#include <stdio.h>
typedef uint64_t u64;
static u64 clock_ms=100000, classifier_until_ms, session_until_ms, classifier_sequence;
static bool diagnostic_only;
static u64 classifier_now_ms(void){return clock_ms;}
static int actual_init_checks(void){
'''
    main='''int main(void){
 unsigned checks=0; diagnostic_only=false; classifier_sequence=1;
 classifier_until_ms=clock_ms+6000;
 const u64 accepted[]={27000,30000,MAXIMUM};
 for(unsigned n=0;n<3;n++){session_until_ms=clock_ms+accepted[n];assert(actual_init_checks()==0);checks++;}
 session_until_ms=clock_ms+MAXIMUM+1;assert(actual_init_checks()==-EINVAL);checks++;
 session_until_ms=clock_ms;assert(actual_init_checks()==-EINVAL);checks++;
 session_until_ms=clock_ms+MAXIMUM;classifier_until_ms=clock_ms+6001;assert(actual_init_checks()==-EINVAL);checks++;
 classifier_until_ms=clock_ms+6000;classifier_sequence=0;assert(actual_init_checks()==-EINVAL);checks++;
 classifier_sequence=1;diagnostic_only=true;assert(actual_init_checks()==-EINVAL);checks++;
 diagnostic_only=false;session_until_ms=0;assert(actual_init_checks()==-EINVAL);checks++;
 classifier_sequence=0;assert(actual_init_checks()==0);checks++;
 printf("actual init boundary checks passed: %u\\n",checks);return 0;
}
'''.replace('MAXIMUM',str(maximum))
    code=prefix+checks+' return 0;\n}\n'+main
    source=root/(label+'-cap.generated.c');source.write_text(code,encoding='utf-8',newline='\n')
    linux='/mnt/c'+source.resolve().as_posix()[2:]
    exe=linux.removesuffix('.c')
    cmd=['wsl.exe','-d','Athena-Cake-Build','--exec']
    build=subprocess.run(cmd+['gcc','-O2','-std=c11','-Wall','-Wextra','-Werror',linux,'-o',exe],capture_output=True)
    (root/(label+'-cap-build.log')).write_bytes(build.stdout+build.stderr)
    assert build.returncode==0,build.stderr
    run=subprocess.run(cmd+[exe],capture_output=True)
    (root/(label+'-cap-run.log')).write_bytes(run.stdout+run.stderr)
    assert run.returncode==0,run.stderr
    results.append({'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                    'maximumMs':maximum,'checks':10,'passed':True})
out={'passed':True,'variants':results,'actualInitChecksExtracted':True,
     'classificationLeaseRemains6000Ms':True,'routerWrites':False,
     'scope':'Actual extracted init code with deterministic clock; not firmware or concurrent kernel behavior'}
(root/'session-cap-qualified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'checks':20,'candidateCapMs':120000,'classifierLeaseMs':6000}))
