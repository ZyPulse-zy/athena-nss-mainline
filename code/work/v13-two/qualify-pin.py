from pathlib import Path
import subprocess,hashlib,json
r=Path(__file__).resolve().parent
source=r/'endpoint-gate/rp_ecm_gate_lab_ct.c'
text=source.read_text();start=text.index('static int pin_instances(void)\n{');a=text.index(' if (!ports[0]',start);b=text.index(' result = parse_nat',a)
condition=text[a:b]
code='''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <errno.h>
#include <stdio.h>
static uint16_t ports[2];static uint32_t marks[2],ids[2];static bool diagnostic_only;
static int actual_checks(void){
'''+condition+'''return 0;}
static void reset(void){ports[0]=1000;ports[1]=1001;marks[0]=0x10000;marks[1]=0x20000;ids[0]=10;ids[1]=11;diagnostic_only=false;}
int main(void){unsigned count=0;reset();assert(actual_checks()==0);count++;
reset();marks[1]=0x10001;assert(actual_checks()==-EINVAL);count++;
reset();marks[1]=0;assert(actual_checks()==-EINVAL);count++;
reset();marks[0]=0;assert(actual_checks()==-EINVAL);count++;
reset();marks[1]=0x0010;assert(actual_checks()==-EINVAL);count++;
reset();marks[1]=0x60000;assert(actual_checks()==-EINVAL);count++;
reset();marks[0]=0x60000;assert(actual_checks()==-EINVAL);count++;
reset();marks[0]|=0x2000;assert(actual_checks()==-EINVAL);count++;
reset();marks[1]|=0x2000;assert(actual_checks()==-EINVAL);count++;
reset();ports[0]=0;assert(actual_checks()==-EINVAL);count++;
reset();ports[1]=0;assert(actual_checks()==-EINVAL);count++;
reset();ids[0]=0;assert(actual_checks()==-EINVAL);count++;
reset();ids[1]=0;assert(actual_checks()==-EINVAL);count++;
reset();marks[0]=0x50001;marks[1]=0x40002;assert(actual_checks()==0);count++;
reset();ids[0]=ids[1]=0;diagnostic_only=true;assert(actual_checks()==0);count++;
printf("actual two-WAN validation checks: %u\\n",count);return 0;}
'''
p=r/'pin.generated.c';p.write_text(code,encoding='utf-8',newline='\n')
linux='/mnt/c'+p.resolve().as_posix()[2:];exe=linux[:-2];prefix=['wsl.exe','-d','Athena-Cake-Build','--exec']
for name,args in [('compile',['gcc','-O2','-std=c11','-Wall','-Wextra','-Werror',linux,'-o',exe]),('run',[exe])]:
 result=subprocess.run(prefix+args,capture_output=True);(r/('pin-'+name+'.log')).write_bytes(result.stdout+result.stderr);assert result.returncode==0,result.stderr
q={'passed':True,'checks':15,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actualPinConditionExtracted':True,'perFlowMarkAndNatSnapshotChecksUnchanged':True,'ctObjectLookupNotModeled':True,'hardwareExecuted':False}
(r/'pin-qualified.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
