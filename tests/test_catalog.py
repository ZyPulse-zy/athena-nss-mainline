# SPDX-License-Identifier: GPL-2.0-only
"""Integrity failures must stop catalog updates rather than bless changed history."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("catalog", REPO / "tools/catalog.py")
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


class CatalogIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.name = "code/work/example/main.py"
        self.data = b"print('original')\n"
        self.write(self.name, self.data)
        self.write("evidence/result.json", b'{"passed":true}\n')
        manifest = {"sources": [{
            "path": self.name,
            "sha256": catalog.digest(self.data),
            "bytes": len(self.data),
        }]}
        self.write("source-manifest.json", catalog.encoded(manifest).encode())
        self.registry = {
            "schema_version": 1,
            "source_manifest_sha256": catalog.digest((self.root / "source-manifest.json").read_bytes()),
            "evidence": {
                "path": "evidence/result.json",
                "sha256": catalog.digest((self.root / "evidence/result.json").read_bytes()),
            },
            "components": [{"id": "main", "path": self.name, "sha256": catalog.digest(self.data)}],
        }
        self.save_registry()

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def save_registry(self):
        self.write("src/current.json", catalog.encoded(self.registry).encode())

    def build(self):
        outputs, _ = catalog.generate(self.root)
        for name, value in outputs.items():
            self.write(name, value.encode())

    def test_unchanged_snapshot_and_catalog_pass(self):
        self.build()
        self.assertEqual(catalog.check(self.root)["source_files"], 1)

    def test_same_length_source_edit_is_rejected(self):
        self.write(self.name, self.data.replace(b"original", b"modified"))
        with self.assertRaisesRegex(ValueError, "Source identity changed"):
            catalog.generate(self.root)

    def test_unlisted_source_cannot_disappear_from_index(self):
        self.write("code/work/another/extra.py", b"pass\n")
        with self.assertRaisesRegex(ValueError, "different files"):
            catalog.generate(self.root)

    def test_python_cache_is_not_an_exported_source(self):
        self.write("code/work/example/__pycache__/main.cpython-311.pyc", b"cache")
        self.build()
        self.assertEqual(catalog.check(self.root)["source_files"], 1)

    def test_stale_generated_index_is_rejected(self):
        self.build()
        self.write("LICENSES/inventory.json", b"{}\n")
        with self.assertRaisesRegex(ValueError, "out of date"):
            catalog.check(self.root)

    def test_changed_evidence_is_rejected(self):
        self.write("evidence/result.json", b'{"passed":false}\n')
        with self.assertRaisesRegex(ValueError, "evidence hash changed"):
            catalog.generate(self.root)

    def test_registry_cannot_reference_parent_directory(self):
        self.registry["components"][0]["path"] = "../outside.py"
        self.save_registry()
        with self.assertRaisesRegex(ValueError, "Invalid repository path"):
            catalog.generate(self.root)

    def test_mismatched_component_hash_is_rejected(self):
        self.registry["components"][0]["sha256"] = "0" * 64
        self.save_registry()
        with self.assertRaisesRegex(ValueError, "not bound"):
            catalog.generate(self.root)

    def test_existing_license_identifiers_and_isc_notice(self):
        self.assertEqual(catalog.source_license(b"// SPDX-License-Identifier: GPL-2.0\n")[0], "GPL-2.0-only")
        header = REPO / "code/work/resident-continuous-dev-20261008/endpoint-gate/ecm_ae_classifier_public.h"
        self.assertEqual(catalog.source_license(header.read_bytes())[:2], ("ISC", "upstream-permission-notice"))

    def test_unrecognized_copyright_requires_review(self):
        with self.assertRaisesRegex(ValueError, "unrecognized source license"):
            catalog.source_license(b"# Copyright 2026 Another Author\n")

    def test_license_expression_is_not_truncated(self):
        with self.assertRaisesRegex(ValueError, "additional SPDX license"):
            catalog.source_license(b"// SPDX-License-Identifier: GPL-2.0-only OR MIT\n")


if __name__ == "__main__":
    unittest.main()
