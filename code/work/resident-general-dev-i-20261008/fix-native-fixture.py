from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'endpoint-gate/ct_harness.py'
s=p.read_text()
a='reset_fixture();tcp2_ct_mark=tcp_ct_mark;CHECK(pin_instances()==0);'
assert s.count(a)==1
s=s.replace(a,'reset_fixture();tcp2_ct_mark=tcp_ct_mark;backing[2].mark=tcp_ct_mark;CHECK(pin_instances()==0);')
# The tuple has two directions; the slot count is not a direction count.
assert s.count('direction < RP11_SLOTS')==1
s=s.replace('direction < RP11_SLOTS','direction < 2')
p.write_text(s)
p=root/'endpoint-gate/build_local.py'
s=p.read_text()
s=s.replace('report["predicate_and_ct_functions_reused"] = True','report["predicate_and_ct_functions_reused"] = False')
s=s.replace('unchanged header and tuple/pin functions; no repeated exhaustive predicate experiment','optional slots changed; all seven nonempty masks covered by extracted control, CT and predicate models')
s=s.replace('new fixed-session AArch64 module','new optional-slot AArch64 module')
p.write_text(s)
p=root/'prepare-runtime.py'
s=(root.parent/'v16-three/prepare-runtime.py').read_text().replace("root.parent/'nss16/compare-runtime-elf.py'","root.parent/'nss16/compare-runtime-elf.py'")
p.write_text(s)
print('fixture corrected; no router connection')
