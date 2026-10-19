#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Index the selected research sources, frozen snapshots and license notices."""

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = (
    "docs/history/snapshots.json",
    "docs/history/README.md",
    "LICENSES/inventory.json",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def repository_file(root, name):
    if not isinstance(name, str) or "\\" in name:
        raise ValueError("Invalid repository path: " + str(name))
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or path.as_posix() != name or ".." in path.parts:
        raise ValueError("Invalid repository path: " + name)
    target = root / name
    if not target.resolve().is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("Missing or external repository file: " + name)
    return target


def source_license(data):
    """Use explicit leading notices; otherwise apply the project default."""
    header = data.decode("utf-8").splitlines()[:24]
    text = "\n".join(header)
    notices = re.findall(
        r"^\s*(?://|/\*|\*|#)?\s*SPDX-License-Identifier:\s*([^\r\n]+)",
        text,
        re.MULTILINE,
    )
    notices = [notice.strip().removesuffix("*/").strip() for notice in notices]
    if notices:
        if set(notices) - {"GPL-2.0", "GPL-2.0-only"}:
            raise ValueError("Register the additional SPDX license: " + ", ".join(notices))
        return "GPL-2.0-only", "spdx-header", notices[0]
    isc = (
        "Copyright (c) 2021, The Linux Foundation.",
        "Copyright (c) 2022-2023 Qualcomm Innovation Center, Inc.",
        "Permission to use, copy, modify, and/or distribute this software for",
        "above copyright notice and this permission notice appear in all copies.",
        'THE SOFTWARE IS PROVIDED "AS IS"',
    )
    if all(part in text for part in isc):
        return "ISC", "upstream-permission-notice", None
    if re.search(r"Copyright|SPDX-License-Identifier|Permission to (use|copy)", text, re.I):
        raise ValueError("Review an unrecognized source license notice")
    return "GPL-2.0-only", "project-default", None


def snapshot_path(path):
    parts = PurePosixPath(path).parts
    if parts[:2] == ("code", "work"):
        return "/".join(parts[:3] if len(parts) > 3 else parts[:2])
    return "/".join(parts[:2])


def natural_order(value):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)]


def generate(root):
    manifest_bytes = repository_file(root, "source-manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    registry_bytes = repository_file(root, "src/current.json").read_bytes()
    registry = json.loads(registry_bytes)
    if registry.get("schema_version") != 1:
        raise ValueError("Unsupported current-source registry version")
    if registry["source_manifest_sha256"] != digest(manifest_bytes):
        raise ValueError("Current registry does not match source-manifest.json")
    evidence = registry["evidence"]
    evidence_bytes = repository_file(root, evidence["path"]).read_bytes()
    if digest(evidence_bytes) != evidence["sha256"]:
        raise ValueError("Current evidence hash changed")
    if not json.loads(evidence_bytes).get("passed"):
        raise ValueError("Selected evidence does not record a passing result")

    sources = {}
    groups = defaultdict(list)
    explicit = []
    counts = Counter()
    for item in manifest["sources"]:
        name = item["path"]
        if name in sources or not name.startswith("code/"):
            raise ValueError("Duplicate or invalid manifest source: " + name)
        data = repository_file(root, name).read_bytes()
        if digest(data) != item["sha256"] or len(data) != item["bytes"]:
            raise ValueError("Source identity changed: " + name)
        license_id, basis, original = source_license(data)
        entry = {
            "path": name,
            "sha256": item["sha256"],
            "bytes": item["bytes"],
            "license": license_id,
            "basis": basis,
        }
        if original:
            entry["original_identifier"] = original
        sources[name] = entry
        groups[snapshot_path(name)].append(entry)
        counts[license_id] += 1
        if basis != "project-default":
            explicit.append(entry)
    actual = {
        p.relative_to(root).as_posix()
        for p in (root / "code").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }
    if actual != set(sources):
        raise ValueError("Code tree and source manifest contain different files")

    components = registry["components"]
    ids = set()
    selected = defaultdict(list)
    for component in components:
        if component["id"] in ids:
            raise ValueError("Duplicate component ID: " + component["id"])
        ids.add(component["id"])
        name = component["path"]
        repository_file(root, name)
        if name not in sources or component["sha256"] != sources[name]["sha256"]:
            raise ValueError("Component is not bound to the source manifest: " + name)
        selected[snapshot_path(name)].append(component["id"])

    snapshots = []
    for name, items in sorted(groups.items(), key=lambda pair: natural_order(pair[0])):
        ordered = sorted(items, key=lambda x: x["path"])
        identities = [{"path": x["path"], "sha256": x["sha256"]} for x in ordered]
        snapshots.append({
            "path": name,
            "files": len(items),
            "bytes": sum(x["bytes"] for x in items),
            "distinct_contents": len({x["sha256"] for x in items}),
            "source_set_sha256": digest(encoded(identities).encode()),
            "selected_components": sorted(selected[name]),
            "licenses": dict(sorted(Counter(x["license"] for x in items).items())),
        })
    workdirs = {p.parts[2] for p in map(PurePosixPath, sources) if p.parts[:2] == ("code", "work") and len(p.parts) > 3}
    summary = {
        "source_files": len(sources),
        "distinct_contents": len({x["sha256"] for x in sources.values()}),
        "work_directories": len(workdirs),
        "indexed_groups": len(snapshots),
        "selected_components": len(components),
    }
    catalog = {
        "schema_version": 1,
        "source_manifest_sha256": digest(manifest_bytes),
        "current_registry_sha256": digest(registry_bytes),
        "summary": summary,
        "snapshots": snapshots,
    }
    inventory = {
        "schema_version": 1,
        "source_manifest_sha256": digest(manifest_bytes),
        "project_default": "GPL-2.0-only",
        "source_license_counts": dict(sorted(counts.items())),
        "explicit_notices": sorted(explicit, key=lambda x: x["path"]),
    }
    lines = [
        "# 源码快照索引", "",
        "由 `python3 tools/catalog.py build` 生成；来源为原始源码清单和主线入口清单。", "",
        f"共 {summary['source_files']:,} 份源文件、{summary['distinct_contents']:,} 种内容，覆盖 {summary['work_directories']} 个逐轮工作目录。", "",
        "[主线入口](../../src/README.md) · [完整索引](snapshots.json) · [原始源码清单](../../source-manifest.json)", "",
        "“主线入口”列列出显式选中的组件。其它快照也可能被导入或用作生成模板；此索引不将它们判定为无依赖文件。原路径与内容哈希保留。", "",
        "| 快照路径 | 文件数 | 不同内容数 | 主线入口 |",
        "| --- | ---: | ---: | --- |",
    ]
    for snapshot in snapshots:
        name = snapshot["path"]
        roles = ", ".join(snapshot["selected_components"]) or "—"
        lines.append(f"| [{name}](../../{name}/) | {snapshot['files']} | {snapshot['distinct_contents']} | {roles} |")
    return {
        OUTPUTS[0]: encoded(catalog),
        OUTPUTS[1]: "\n".join(lines) + "\n",
        OUTPUTS[2]: encoded(inventory),
    }, summary


def check(root):
    outputs, summary = generate(root)
    for name, expected in outputs.items():
        path = repository_file(root, name)
        if path.read_text(encoding="utf-8") != expected:
            raise ValueError("Catalog is out of date: " + name)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("show", "build", "check"))
    args = parser.parse_args()
    try:
        if args.command == "show":
            registry = json.loads((ROOT / "src/current.json").read_text(encoding="utf-8"))
            print(registry["snapshot_id"], registry["snapshot_date"])
            for component in registry["components"]:
                print(component["id"] + ": " + component["path"])
            return
        if args.command == "check":
            summary = check(ROOT)
        else:
            outputs, summary = generate(ROOT)
            for name, content in outputs.items():
                target = ROOT / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8", newline="\n")
        print(encoded({"passed": True, **summary}).strip())
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    main()
