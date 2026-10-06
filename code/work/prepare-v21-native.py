"""Five immutable CT objects, one naturally distinct WAN each. No router writes."""
from pathlib import Path
w=Path(__file__).resolve().parents[1];old=w/'work/v16-three/endpoint-gate';root=w/'work/v21-fiveflow';root.mkdir();gate=root/'endpoint-gate';gate.mkdir()
for f in ['Makefile','two_slot_predicate.h','predicate_test.c','rp_ecm_gate_lab_ct.c','ecm_ae_classifier_public.h','control_harness.py','ct_harness.py','build_local.py']:(gate/f).write_bytes((old/f).read_bytes())
p=gate/'two_slot_predicate.h';s=p.read_text().replace('RP11_TCP2 = 2','RP11_TCP2 = 2, RP11_TCP3 = 3, RP11_TCP4 = 4').replace('#define RP11_SLOTS 3','#define RP11_SLOTS 5')
needle='    rp11_u16 tcp2_source_port, tcp2_server_port;';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    rp11_u32 tcp3_server, tcp4_server;\n    rp11_u16 tcp3_source_port, tcp3_server_port, tcp4_source_port, tcp4_server_port;')
a=s.index('    return c &&',s.index('static inline int rp11_config_valid'));b=s.index('\n}',a)
s=s[:a]+'''    if (!c || !rp11_game_server_valid(c->game_server) || !c->game_source_port || !c->game_server_port) return 0;
    rp11_u32 hosts[4]={c->tcp_server,c->tcp2_server,c->tcp3_server,c->tcp4_server};
    rp11_u16 source[4]={c->tcp_source_port,c->tcp2_source_port,c->tcp3_source_port,c->tcp4_source_port};
    rp11_u16 dest[4]={c->tcp_server_port,c->tcp2_server_port,c->tcp3_server_port,c->tcp4_server_port};
    for (unsigned n=0;n<4;n++) { if (!rp11_game_server_valid(hosts[n]) || !source[n] || !dest[n]) return 0;
        for(unsigned m=0;m<n;m++) if(hosts[n]==hosts[m] && source[n]==source[m] && dest[n]==dest[m]) return 0; }
    return 1;'''+s[b:]
a=s.index('    if (protocol == 6 &&',s.index('return RP11_TCP;'));b=s.index('    if (protocol == 17 &&',a);block=s[a:b]
s=s[:b]+''.join(block.replace('tcp2','tcp'+str(n)).replace('RP11_TCP2','RP11_TCP'+str(n)) for n in [3,4])+s[b:]
s=s.replace('struct rp11_tuple out[6]','struct rp11_tuple out[10]');needle='        c->tcp2_server_port, c->tcp2_source_port, 6};';assert s.count(needle)==1
s=s.replace(needle,needle+''.join('\n    out[%d] = (struct rp11_tuple){RP11_CLIENT, c->tcp%d_server, c->tcp%d_source_port, c->tcp%d_server_port, 6};\n    out[%d] = (struct rp11_tuple){c->tcp%d_server, RP11_CLIENT, c->tcp%d_server_port, c->tcp%d_source_port, 6};'%(2*n,n,n,n,2*n+1,n,n,n) for n in [3,4]));p.write_text(s)
p=gate/'rp_ecm_gate_lab_ct.c';s=p.read_text();lines=s.splitlines(keepends=True);out=[]
for line in lines:
 out.append(line)
 if (line.startswith('static ') and 'tcp2_' in line and ';' in line) or (line.startswith('module_param') and ('tcp2_' in line or 'RP11_TCP2' in line)):
  out.extend(line.replace('tcp2','tcp'+str(n)).replace('RP11_TCP2','RP11_TCP'+str(n)) for n in [3,4])
s=''.join(out);needle='   .expiry_runs = ATOMIC64_INIT(0), .deny_events = ATOMIC64_INIT(0) }\n};';assert s.count(needle)==1
s=s.replace(needle,'   .expiry_runs = ATOMIC64_INIT(0), .deny_events = ATOMIC64_INIT(0) },\n'+',\n'.join(' { .index = RP11_TCP%d, .eligible = ATOMIC64_INIT(0), .allowed = ATOMIC64_INIT(0),\n   .expiry_runs = ATOMIC64_INIT(0), .deny_events = ATOMIC64_INIT(0) }'%n for n in [3,4])+'\n};')
s=s.replace('struct rp11_tuple t[6]','struct rp11_tuple t[10]')
for f in ['nat_port','ct_id_raw','ct_mark']:s=s.replace('game_'+f+', tcp2_'+f+' };','game_'+f+', tcp2_'+f+', tcp3_'+f+', tcp4_'+f+' };')
needle=' if (((marks[0] >> 16) & 255) == ((marks[2] >> 16) & 255)) return -EINVAL;';assert s.count(needle)==1
s=s.replace(needle,' for (n=0;n<RP11_SLOTS;n++) { unsigned int m; for(m=0;m<n;m++)\n  if (((marks[n] >> 16) & 255) == ((marks[m] >> 16) & 255)) return -EINVAL; }')
needle=' result = parse_nat(tcp2_nat_address, &nat[2]); if (result) return result;';assert s.count(needle)==1
s=s.replace(needle,needle+'\n result = parse_nat(tcp3_nat_address, &nat[3]); if (result) return result;\n result = parse_nat(tcp4_nat_address, &nat[4]); if (result) return result;')
s=s.replace('__be32 address, tcp_address, tcp2_address;','__be32 address, tcp_address, tcp2_address, tcp3_address, tcp4_address;')
s=s.replace('if (!tcp2_server || !*tcp2_server ||','if (!tcp3_server || !*tcp3_server || !tcp4_server || !*tcp4_server || !tcp2_server || !*tcp2_server ||')
needle=' if (!in4_pton(tcp2_server, -1, (u8 *)&tcp2_address, -1, &end) || !end || *end) return -EINVAL;';assert s.count(needle)==1
s=s.replace(needle,needle+'\n'+''.join(needle.replace('tcp2','tcp'+str(n))+'\n' for n in [3,4]).rstrip())
s=s.replace('ntohl(tcp2_address), tcp2_source_port, tcp2_server_port};','ntohl(tcp2_address), tcp2_source_port, tcp2_server_port, ntohl(tcp3_address), ntohl(tcp4_address), tcp3_source_port, tcp3_server_port, tcp4_source_port, tcp4_server_port};')
s=s.replace('Holds at most three refs','Holds at most five refs').replace('three exact immutable IPv4 routed slots','five exact immutable IPv4 routed slots').replace('v16-three-exact-120s-DRAFT','v21-five-exact-120s-DRAFT');p.write_text(s)
extra='RP11_TCP_SERVER,RP11_TCP_SERVER,47778,443,47779,443'
p=gate/'predicate_test.c';s=p.read_text().replace('RP11_TCP_SERVER,47777,443}', 'RP11_TCP_SERVER,47777,443,'+extra+'}').replace('t[6]','t[10]').replace('n<6','n<10').replace('three-slot','five-slot');p.write_text(s)
p=gate/'control_harness.py';s=p.read_text().replace('RP11_TCP_SERVER,47777,RP11_TCP_DPORT}','RP11_TCP_SERVER,47777,RP11_TCP_DPORT,'+extra+'}').replace('struct rp11_tuple t[6]','struct rp11_tuple t[10]').replace('struct rp11_tuple tuples[6]','struct rp11_tuple tuples[10]').replace('n<6','n<10').replace('return visible_ci[0]+visible_ci[1]+visible_ci[2];','unsigned sum=0;for(unsigned n=0;n<RP11_SLOTS;n++)sum+=visible_ci[n];return sum;').replace('p[3]={{&slots[0]},{&slots[1]},{&slots[2]}}','p[5]={{&slots[0]},{&slots[1]},{&slots[2]},{&slots[3]},{&slots[4]}}').replace('revoke_calls==6','revoke_calls==10').replace('worker(0);worker(1);worker(2);','worker(0);worker(1);worker(2);worker(3);worker(4);').replace('three-slot','five-slot');p.write_text(s)
p=gate/'ct_harness.py';s=p.read_text().replace('backing[4]','backing[6]').replace('hash_slots[3]','hash_slots[5]').replace('direction < RP11_SLOTS','direction < 2').replace('n<3','n<5').replace('struct rp11_tuple t[6]','struct rp11_tuple t[10]').replace('RP11_TCP_SERVER,47777,443}','RP11_TCP_SERVER,47777,443,'+extra+'}')
s=s.replace('tcp2_ct_id_raw, tcp_ct_mark','tcp2_ct_id_raw, tcp3_ct_id_raw, tcp4_ct_id_raw, tcp_ct_mark').replace('game_ct_mark, tcp2_ct_mark;','game_ct_mark, tcp2_ct_mark, tcp3_ct_mark, tcp4_ct_mark;').replace('*tcp2_nat_address;','*tcp2_nat_address, *tcp3_nat_address, *tcp4_nat_address;').replace('game_nat_port, tcp2_nat_port;','game_nat_port, tcp2_nat_port, tcp3_nat_port, tcp4_nat_port;')
s=s.replace('tcp2_ct_id_raw=13;tcp_ct_mark=0x10000;game_ct_mark=0x10000;tcp2_ct_mark=0x20000;', 'tcp2_ct_id_raw=13;tcp3_ct_id_raw=14;tcp4_ct_id_raw=15;tcp_ct_mark=0x10000;game_ct_mark=0x20000;tcp2_ct_mark=0x30000;tcp3_ct_mark=0x40000;tcp4_ct_mark=0x50000;')
s=s.replace('tcp_nat_address=game_nat_address=tcp2_nat_address=', 'tcp_nat_address=game_nat_address=tcp2_nat_address=tcp3_nat_address=tcp4_nat_address=').replace('tcp2_nat_port=47777;', 'tcp2_nat_port=47777;tcp3_nat_port=47778;tcp4_nat_port=47779;').replace('ct->mark=n==2?0x20000:0x10000;', 'ct->mark=(n+1)<<16;').replace('gets==6&&put_calls==3','gets==10&&put_calls==5').replace('three-slot','five-slot')
# The old three-slot harness iterated three tuple directions for a two-direction kernel structure.
# Fix only this new model; preserve the historic model and all real hardware evidence.
p.write_text(s)
p=gate/'build_local.py';s=p.read_text().replace('v16-three-exact','v21-five-exact');p.write_text(s)
print('Five-slot native source and extracted-C models prepared; no hardware writes')
