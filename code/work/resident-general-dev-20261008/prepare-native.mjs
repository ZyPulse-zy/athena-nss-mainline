import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';
const root='work/resident-general-dev-20261008',gate=root+'/endpoint-gate',old='work/v16-three/endpoint-gate';
fs.mkdirSync(gate);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const files=['Makefile','two_slot_predicate.h','predicate_test.c','rp_ecm_gate_lab_ct.c','ecm_ae_classifier_public.h','control_harness.py','ct_harness.py','build_local.py'];
const baseline={};for(const n of files){const b=fs.readFileSync(old+'/'+n);baseline[n]=hash(b);fs.writeFileSync(gate+'/'+n,b,{flag:'wx'});}
fs.writeFileSync(root+'/native-original-shas.json',JSON.stringify(baseline,null,2)+'\n',{flag:'wx'});
const once=(s,a,b)=>{assert.equal(s.split(a).length,2,a);return s.replace(a,()=>b);};
let h=fs.readFileSync(gate+'/two_slot_predicate.h','utf8').replaceAll('\r\n','\n');
const start=h.indexOf('static inline int rp11_config_valid('),end=h.indexOf('static inline enum rp11_slot rp11_match(',start);assert.ok(end>start);
h=h.slice(0,start)+`static inline int rp11_slot_enabled(const struct rp11_config *c, unsigned n)
{
 return c && (n == RP11_TCP ? c->tcp_server != 0 : n == RP11_GAME ? c->game_server != 0 : n == RP11_TCP2 ? c->tcp2_server != 0 : 0);
}
static inline int rp11_config_valid(const struct rp11_config *c)
{
 if (!c) return 0;
 if (c->tcp_server ? !rp11_game_server_valid(c->tcp_server) || !c->tcp_source_port || !c->tcp_server_port : c->tcp_source_port || c->tcp_server_port) return 0;
 if (c->game_server ? !rp11_game_server_valid(c->game_server) || !c->game_source_port || !c->game_server_port : c->game_source_port || c->game_server_port) return 0;
 if (c->tcp2_server ? !rp11_game_server_valid(c->tcp2_server) || !c->tcp2_source_port || !c->tcp2_server_port : c->tcp2_source_port || c->tcp2_server_port) return 0;
 if (!c->tcp_server && !c->game_server && !c->tcp2_server) return 0;
 return !c->tcp_server || !c->tcp2_server || c->tcp_server != c->tcp2_server || c->tcp_source_port != c->tcp2_source_port || c->tcp_server_port != c->tcp2_server_port;
}
`+h.slice(end);
h=h.replace('if (protocol == 6 &&','if (c->tcp_server && protocol == 6 &&');
const second=h.indexOf('if (protocol == 6 &&');assert.ok(second>0);h=h.slice(0,second)+h.slice(second).replace('if (protocol == 6 &&','if (c->tcp2_server && protocol == 6 &&');
h=once(h,'if (protocol == 17 &&','if (c->game_server && protocol == 17 &&');
fs.writeFileSync(gate+'/two_slot_predicate.h',h);
let c=fs.readFileSync(gate+'/rp_ecm_gate_lab_ct.c','utf8').replaceAll('\r\n','\n');
c=once(c,'static bool diagnostic_only = true;','/* Frozen subset: TCP=1, UDP RT=2, second TCP=4. Disabled slots never pin or admit. */\nstatic unsigned int active_slots = 7;\nmodule_param(active_slots, uint, 0400);\nstatic bool diagnostic_only = true;');
c=once(c,'if (!READ_ONCE(registered) || !smp_load_acquire(&s->admit)) return false;','if (!rp11_slot_enabled(&immutable_config, s->index) || !READ_ONCE(registered) || !smp_load_acquire(&s->admit)) return false;');
c=once(c,' s->cpu_drain_ticket = false;\n synchronize_net();',' if (!rp11_slot_enabled(&immutable_config, s->index)) { s->cpu_drain_ticket = true; return; }\n s->cpu_drain_ticket = false;\n synchronize_net();');
c=once(c,'if (!initialized || !registered || teardown || s->terminal || s->ever_opened) {','if (!initialized || !registered || teardown || !rp11_slot_enabled(&immutable_config, s->index) || s->terminal || s->ever_opened) {');
c=once(c,'  if (!lease_now(&slots[n]) || !instance_ready(n)) {','  if (rp11_slot_enabled(&immutable_config, n) && (!lease_now(&slots[n]) || !instance_ready(n))) {');
c=once(c,' for (n = 0; n < RP11_SLOTS; ++n)\n  WRITE_ONCE(slots[n].deadline,',' for (n = 0; n < RP11_SLOTS; ++n) if (rp11_slot_enabled(&immutable_config, n))\n  WRITE_ONCE(slots[n].deadline,');
c=once(c,' for (n = 0; n < RP11_SLOTS; ++n) smp_store_release(&slots[n].admit, true);',' for (n = 0; n < RP11_SLOTS; ++n) if (rp11_slot_enabled(&immutable_config, n)) smp_store_release(&slots[n].admit, true);');
const a=c.indexOf(' for (n = 0; n < RP11_SLOTS; ++n)\n  if (!ports[n]'),b=c.indexOf(' /* Each immutable slot',a);assert.ok(b>a);
c=c.slice(0,a)+` const char *nat_text[RP11_SLOTS] = { tcp_nat_address, game_nat_address, tcp2_nat_address };
 for (n = 0; n < RP11_SLOTS; ++n) {
  if (!rp11_slot_enabled(&immutable_config, n)) {
   if (ports[n] || marks[n] || ids[n] || (nat_text[n] && *nat_text[n])) return -EINVAL;
   nat[n] = 0; continue;
  }
  if (!ports[n] || !marks[n] || ((marks[n] >> 16) & 255) < 1 || ((marks[n] >> 16) & 255) > 5 || (marks[n] & 0x2000) || (!diagnostic_only && !ids[n])) return -EINVAL;
  result = parse_nat(nat_text[n], &nat[n]); if (result) return result;
 }
`+c.slice(b);
c=once(c,'  struct pinned_identity *p = &pinned[n];\n  struct nf_conntrack_tuple_hash *h;','  struct pinned_identity *p = &pinned[n];\n  struct nf_conntrack_tuple_hash *h;');
c=once(c,'  fill_tuple(&p->original, &t[n * 2], IP_CT_DIR_ORIGINAL);','  if (!rp11_slot_enabled(&immutable_config, n)) continue;\n  fill_tuple(&p->original, &t[n * 2], IP_CT_DIR_ORIGINAL);');
c=once(c,' __be32 address, tcp_address, tcp2_address;',' __be32 address = 0, tcp_address = 0, tcp2_address = 0;');
const i=c.indexOf(' if (!tcp2_server ||'),j=c.indexOf(' if (!rp11_config_valid',i);assert.ok(j>i);
c=c.slice(0,i)+` if (!active_slots || (active_slots & ~7U) || !register_gate || !digest_format_valid(frozen_record_sha256)) return -EACCES;
 if (active_slots & 1U) { if (!tcp_server || !*tcp_server || !in4_pton(tcp_server, -1, (u8 *)&tcp_address, -1, &end) || !end || *end) return -EINVAL; }
 else if ((tcp_server && *tcp_server) || tcp_source_port || tcp_server_port) return -EINVAL;
 if (active_slots & 2U) { if (!game_server || !*game_server || !in4_pton(game_server, -1, (u8 *)&address, -1, &end) || !end || *end) return -EINVAL; }
 else if ((game_server && *game_server) || game_source_port || game_server_port) return -EINVAL;
 if (active_slots & 4U) { if (!tcp2_server || !*tcp2_server || !in4_pton(tcp2_server, -1, (u8 *)&tcp2_address, -1, &end) || !end || *end) return -EINVAL; }
 else if ((tcp2_server && *tcp2_server) || tcp2_source_port || tcp2_server_port) return -EINVAL;
 immutable_config = (struct rp11_config){ntohl(address), game_source_port, game_server_port, ntohl(tcp_address), tcp_source_port, tcp_server_port, ntohl(tcp2_address), tcp2_source_port, tcp2_server_port};
`+c.slice(j);
fs.writeFileSync(gate+'/rp_ecm_gate_lab_ct.c',c);
for(const [n,d]of Object.entries(baseline))assert.equal(hash(fs.readFileSync(old+'/'+n)),d);
console.log(JSON.stringify({prepared:true,oldSourcesUnchanged:true,productionWrites:false}));
