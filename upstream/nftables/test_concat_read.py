"""Compile the actual concat read functions with real built libnftables helpers.

No kernel or Netlink socket. --fixed evaluates the proposed three-line change.
The manually constructed typeof key is not a complete kernel round trip.
"""
import argparse,json,pathlib,subprocess,tempfile
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--fixed',action='store_true');p.add_argument('--output',type=pathlib.Path)
p.add_argument('--source',required=True,type=pathlib.Path)
p.add_argument('--build',required=True,type=pathlib.Path)
p.add_argument('--prefix',required=True,type=pathlib.Path)
a=p.parse_args();source=a.source;build=a.build;prefix=a.prefix
text=(source/'src/netlink.c').read_text()
def block(anchor):
    s=text.index(anchor);e=text.index('{',s)+1;d=1
    while d:d+=(text[e]=='{')-(text[e]=='}');e+=1
    return text[s:e]
code=block('static struct expr *concat_elem_expr(')+'\n'+block('static struct expr *netlink_parse_concat_elem_key(')
if a.fixed:
    old='if (set->key->etype == EXPR_CONCAT)\n\t\tn = list_first_entry(&expr_concat(set->key)->expressions, struct expr, list);'
    new='if (set->key->etype == EXPR_CONCAT) {\n\t\toff = expr_concat(set->key)->size;\n\t\tn = list_first_entry(&expr_concat(set->key)->expressions, struct expr, list);\n\t}'
    assert code.count(old)==1;code=code.replace(old,new)
test=r'''
#include <nft.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <expression.h>
#include <datatype.h>
#include <rule.h>
#include <netlink.h>
#include <utils.h>
#include <gmputil.h>
'''+code+r'''
int main(void) {
 struct location loc={0};struct set set={0};uint32_t packed=0;
 unsigned types[]={TYPE_INTEGER,TYPE_MARK,TYPE_INET_PROTOCOL,TYPE_IPADDR,TYPE_INET_SERVICE,
  TYPE_IPADDR,TYPE_INET_SERVICE,TYPE_IPADDR,TYPE_INET_SERVICE,TYPE_IPADDR,TYPE_INET_SERVICE};
 unsigned bits[]={32,32,8,32,16,32,16,32,16,32,16};
 set.key=concat_expr_alloc(&loc);
 for(unsigned i=0;i<11;i++) {
  const struct datatype *dt=datatype_lookup(types[i]);uint32_t value=i+1;
  struct expr *key=constant_expr_alloc(&loc,dt,dt->byteorder,bits[i],&value);
  concat_expr_add(set.key,key);packed=concat_subtype_add(packed,types[i]);
 }
 set.key->dtype=concat_type_alloc(packed);set.key->len=352;
 uint8_t bytes[44]={0};for(unsigned i=0;i<sizeof(bytes);i++)bytes[i]=i+1;
 struct expr *data=constant_expr_alloc(&loc,&integer_type,BYTEORDER_BIG_ENDIAN,352,bytes);
 struct expr *decoded=netlink_parse_concat_elem_key(&set,data);
 unsigned count=expr_concat(decoded)->size;
 printf("{\"inputFields\":11,\"packedSubtypeCount\":%u,\"decodedFields\":%u,\"passed\":%s,\"kernelNetlinkTested\":false}\n",set.key->dtype->subtypes,count,count==11?"true":"false");
 expr_free(decoded);expr_free(set.key);return count==11?0:1;
}
'''
with tempfile.TemporaryDirectory() as d:
    c=pathlib.Path(d)/'read-test.c';b=c.with_suffix('');c.write_text(test)
    subprocess.run(['cc','-Wall','-Wextra','-Werror','-DHAVE_CONFIG_H', '-I'+str(build),
        '-I'+str(source/'include'),'-I'+str(prefix/'include'),str(c),str(build/'src/.libs/libnftables.a'),
        '-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib'),'-lnftnl','-lmnl','-lgmp','-ljansson','-o',str(b)],check=True)
    r=subprocess.run([str(b)],text=True,capture_output=True)
    if not r.stdout:raise RuntimeError(r.stderr)
    result=json.loads(r.stdout);result['candidateChangeApplied']=a.fixed
    if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));raise SystemExit(r.returncode)
