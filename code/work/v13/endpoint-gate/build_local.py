#!/usr/bin/env python3
"""Local independent build/inspection. No router, network or module loading."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[2]
SDK = Path("/opt/athena/sdk")
KERNEL = SDK / "build_dir/target-aarch64_cortex-a53_musl/linux-qualcommax_ipq60xx/linux-6.18.44"
TC = SDK / "staging_dir/toolchain-aarch64_cortex-a53_gcc-14.4.0_musl/bin"
ECM = BASE / "work/ecm.ko"
SOURCES = ["Makefile", "two_slot_predicate.h", "predicate_test.c", "rp_ecm_gate_lab_ct.c", "ecm_ae_classifier_public.h", "control_harness.py", "ct_harness.py"]
EXPORTS = ["ecm_ae_classifier_ops_register", "ecm_ae_classifier_ops_unregister",
           "ecm_ae_classifier_decelerate_v4_connection", "ecm_db_connection_count_get"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def snapshot(root):
    files, links = {}, {}
    for current, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            p = Path(current) / name
            rel = str(p.relative_to(root))
            if p.is_symlink():
                links[rel] = os.readlink(p)
            elif p.is_file():
                files[rel] = sha(p)
    return {"files": files, "symlinks": links}


def run(args, log=None, cwd=None, env=None):
    r = subprocess.run(args, cwd=cwd, env=env, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log:
        (HERE / log).write_text(r.stdout)
    if r.returncode:
        raise RuntimeError(f"command exited {r.returncode}; log={log}: {args[0]}")
    return r.stdout


def main():
    report = {"schema": "v13-two-wan-private-build", "router_connected": False,
              "modules_loaded": False, "live_permit_implemented": True,
              "executed_build_script_sha256": sha(Path(__file__)),
              "source_hashes": {n: sha(HERE / n) for n in SOURCES},
              "ecm_sha256": sha(ECM), "kernel_key_hashes": {n: sha(KERNEL / n) for n in
                [".config", "Module.symvers", "include/generated/autoconf.h", "include/config/kernel.release",
                 "include/generated/utsrelease.h", "include/linux/netfilter.h"]},
              "frozen_inputs": {str(p.relative_to(BASE)): sha(p) for p in
                [BASE / "work/nss7/rp_ecm_gate.ko", BASE / "work/nss10/tcp-udp-gate/rp_ecm_gate_tcp_udp.ko",
                 BASE / "work/nss10/tcp-udp-gate/build-manifest.json",
                 BASE / "work/nss11/tag-gate-review/rp_ecm_gate_game_deny.ko",
                 BASE / "work/nss11/tag-gate-review/build-manifest.json",
                 BASE / "work/nss11/tag-gate-review/SHA256SUMS"]}}
    before = snapshot(KERNEL)
    (HERE / "sdk-original-before.json").write_text(json.dumps(before))
    report["sdk_counts"] = {"files": len(before["files"]), "symlinks": len(before["symlinks"])}
    root = Path(tempfile.mkdtemp(prefix="athena-v13-two-wan-"))
    report["private_build_root"] = str(root)
    private_kernel, private_module = root / "kernel", root / "module"
    try:
        config = (KERNEL / ".config").read_text().splitlines()
        assert "CONFIG_ARM64=y" in config and "# CONFIG_MODVERSIONS is not set" in config
        assert all(s in config for s in ["CONFIG_NF_CONNTRACK=m", "CONFIG_NF_CONNTRACK_MARK=y", "CONFIG_NF_CONNTRACK_ZONES=y", "CONFIG_NF_NAT=m"])
        assert (KERNEL / "include/config/kernel.release").read_text().strip() == "6.18.44"
        report["config_lines"] = [s for s in config if any(k in s for k in
            ["CONFIG_ARM64=", "CONFIG_SMP=", "CONFIG_MODULES=", "CONFIG_MODULE_UNLOAD=", "CONFIG_MODVERSIONS",
             "CONFIG_MODULE_SIG", "CONFIG_RANDSTRUCT", "CONFIG_MODULE_STRIPPED", "CONFIG_NETFILTER=", "CONFIG_NF_CONNTRACK=", "CONFIG_NF_CONNTRACK_MARK=", "CONFIG_NF_CONNTRACK_ZONES=", "CONFIG_NF_NAT="])]
        env = os.environ.copy()
        env["PATH"] = str(TC) + ":" + env["PATH"]
        env["STAGING_DIR"] = str(SDK / "staging_dir")
        nm = run([str(TC / "aarch64-openwrt-linux-musl-nm"), str(ECM)], "ecm-nm.txt")
        relocs = run([str(TC / "aarch64-openwrt-linux-musl-readelf"), "-Wr", str(ECM)], "ecm-relocations.txt")
        ksym = relocs.split("Relocation section '.rela__ksymtab'", 1)[1].split("\nRelocation section ", 1)[0]
        records = {}
        for line in ksym.splitlines():
            fields = line.split()
            if len(fields) == 7 and fields[2] == "R_AARCH64_PREL32":
                records[int(fields[0], 16)] = fields[4]
        report["actual_ecm_export_triples"] = {}
        for symbol in EXPORTS:
            offsets = [off for off, target in records.items() if target == symbol]
            assert len(offsets) == 1 and "__kstrtab_" + symbol in nm
            off = offsets[0]
            assert records.get(off + 4) == "__kstrtab_" + symbol and records.get(off + 8) == "__kstrtabns_" + symbol
            report["actual_ecm_export_triples"][symbol] = [hex(off), hex(off + 4), hex(off + 8)]
        for function in ["ecm_ae_classifier_ops_unregister", "ecm_ported_ipv4_process", "ecm_ipv4_ip_process", "ecm_ipv4_post_routing_hook"]:
            run([str(TC / "aarch64-openwrt-linux-musl-objdump"), "-dr", "--disassemble=" + function, str(ECM)], "binary-" + function + ".txt")
        run([str(TC / "aarch64-openwrt-linux-musl-readelf"), "--string-dump=.modinfo", str(ECM)], "binary-ecm-modinfo.txt")
        print("Saved actual ECM scoped disassembly; copying prepared kernel privately", flush=True)
        shutil.copytree(KERNEL, private_kernel, symlinks=True)
        private_module.mkdir()
        report["private_wrapper_relocations"] = []
        for wrapper in ["scripts/basic/fixdep", "scripts/mod/modpost"]:
            p = private_kernel / wrapper
            text = p.read_text()
            old = "$dir/../../../../../../staging_dir/host/lib"
            assert old in text
            p.write_text(text.replace(old, str(SDK / "staging_dir/host/lib")))
            report["private_wrapper_relocations"].append(wrapper)
        for name in SOURCES:
            shutil.copy2(HERE / name, private_module / name)
        symvers = "".join("0x00000000\t" + s + "\tecm\tEXPORT_SYMBOL\t\n" for s in EXPORTS)
        (private_module / "ecm-exports.symvers").write_text(symvers)
        (HERE / "ecm-exports.symvers").write_text(symvers)
        report["symvers_origin"] = "locally reconstructed actual export names; CRC0 non-MODVERSIONS dependency records; not authentic ECM build CRC/ABI proof"
        report["predicate_and_ct_functions_reused"] = True
        report["historical_predicate_scope"] = "unchanged header and tuple/pin functions; no repeated exhaustive predicate experiment"
        report["offline_tests"] = run(["python3", "control_harness.py"], "control-harness-build-run.log", HERE)
        print("Extracted control checks passed; compiling new fixed-session AArch64 module", flush=True)
        build = run(["make", "-C", str(private_kernel), "M=" + str(private_module), "ARCH=arm64",
                     "CROSS_COMPILE=aarch64-openwrt-linux-musl-", "KBUILD_EXTRA_SYMBOLS=" + str(private_module / "ecm-exports.symvers"), "modules"],
                    "module-build.log", env=env)
        for p in private_module.iterdir():
            if p.is_file() and p.name not in SOURCES and p.name != "predicate-test-host":
                shutil.copy2(p, HERE / p.name)
        module = HERE / "rp_ecm_gate_lab_ct.ko"
        report["module_sha256"] = sha(module)
        report["module_modinfo"] = run([str(TC / "aarch64-openwrt-linux-musl-readelf"), "--string-dump=.modinfo", str(module)], "module-modinfo.txt")
        imports = run([str(TC / "aarch64-openwrt-linux-musl-nm"), "-u", str(module)], "module-imports.txt")
        names = {s.split()[-1] for s in imports.splitlines()}
        kernel_exports = {s.split()[1] for s in (KERNEL / "Module.symvers").read_text().splitlines() if len(s.split()) >= 2}
        report["imports"] = sorted(names)
        report["unresolved_metadata_imports"] = sorted(names - kernel_exports - set(EXPORTS))
        assert not report["unresolved_metadata_imports"]
        sections = run([str(TC / "aarch64-openwrt-linux-musl-readelf"), "-S", str(module)], "module-sections.txt")
        report["versions_section_present"] = "__versions" in sections
        report["module_warnings"] = [s for s in build.splitlines() if "WARNING:" in s]
        run([str(TC / "aarch64-openwrt-linux-musl-objdump"), "-dr", "--disassemble=select_exact", str(module)], "binary-select_exact.txt")
        report["status"] = "built-classifier-epoch-offline; no runtime qualification"
    except Exception as e:
        report["status"] = "failed"
        report["error"] = str(e)
    finally:
        after = snapshot(KERNEL)
        (HERE / "sdk-original-after.json").write_text(json.dumps(after))
        report["sdk_original_unchanged"] = before == after
        report["old_gate_inputs_unchanged"] = all(sha(BASE / n) == h for n, h in report["frozen_inputs"].items())
        report["source_inputs_unchanged"] = all(sha(HERE / n) == h for n, h in report["source_hashes"].items())
        (HERE / "build-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
        print(report["status"], flush=True)
        return report["status"] == "built-classifier-epoch-offline; no runtime qualification"


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
