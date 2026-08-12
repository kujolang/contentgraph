#!/usr/bin/env python3
from __future__ import annotations
import json
import hashlib
import random
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/"src"/"contentgraph.py"


class ContentGraphTests(unittest.TestCase):
    def run_cli(self,*args,expected=0):
        result=subprocess.run(["python3",str(CLI),*map(str,args)],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(expected,result.returncode,result.stderr+result.stdout); return result

    def siteprobe_fixture(self,root:Path):
        pages=[
            {"url":"https://example.com/","final_url":"https://example.com/","canonical":"https://example.com/","title":"Home","meta_description":"Kujo site","headings":{"h1":["Home"]},"content_fingerprint":"a","content_type":"text/html","incoming_link_count":0,"outgoing_link_count":2,"depth":0,"sitemap_member":True,"internal_links":[{"url":"https://example.com/guide-a"},{"url":"https://example.com/typography"}]},
            {"url":"https://example.com/guide-a","final_url":"https://example.com/guide-a","canonical":"https://example.com/guide-a","title":"Kujo Agent Workflows","meta_description":"Evidence workflows","headings":{"h1":["Kujo Agent Workflows"]},"content_fingerprint":"b","content_type":"text/html","incoming_link_count":1,"outgoing_link_count":0,"depth":1,"sitemap_member":True,"internal_links":[]},
            {"url":"https://example.com/orphan","final_url":"https://example.com/orphan","canonical":"https://example.com/orphan","title":"Agent Workflow Evidence","meta_description":"Deterministic evidence workflows","headings":{"h1":["Agent Workflow Evidence"]},"content_fingerprint":"c","content_type":"text/html","incoming_link_count":0,"outgoing_link_count":0,"depth":1,"sitemap_member":True,"internal_links":[]},
        ]
        root.mkdir(); (root/"pages.jsonl").write_text("".join(json.dumps(x)+"\n" for x in pages)); (root/"links.json").write_text(json.dumps({"links":[{"source":"https://example.com/","target":"https://example.com/guide-a","text":"Guide","rel":"","internal":True}]}))

    def test_source_build_relationships_and_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/"run"
            self.run_cli("build","--source",ROOT/"fixtures/source","--out",run,"--overlap-threshold","0.25","--json")
            graph=json.loads((run/"graph.json").read_text()); self.assertEqual("contentgraph.graph/v1",graph["schema"]); self.assertEqual(3,len(graph["nodes"]))
            self.assertTrue(json.loads((run/"overlaps.json").read_text())["overlaps"])
            self.assertTrue(json.loads((run/"link-opportunities.json").read_text())["opportunities"])
            self.assertIn("graphml",self.run_cli("export",run,"--format","graphml").stdout)
            nodes=[json.loads(x) for x in (run/"nodes.jsonl").read_text().splitlines()]
            self.run_cli("inspect",run,"--node",nodes[0]["id"])
            related=json.loads(self.run_cli("related",run,"--node",nodes[0]["id"]).stdout)["related"]
            self.assertEqual(related, sorted(related, key=lambda x: (-x["score"], x["node_id"])))
            export=Path(tmp)/"graph.graphml"
            self.run_cli("export",run,"--format","graphml","--out",export)
            self.run_cli("export",run,"--format","graphml","--out",export,expected=1)
            self.run_cli("export",run,"--format","graphml","--out",export,"--force")
            self.assertIn('<key id="title"', export.read_text())

    def test_siteprobe_ingestion_orphans_and_compare(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); probe=root/"probe"; self.siteprobe_fixture(probe); run1=root/"one"; run2=root/"two"
            self.run_cli("build","--siteprobe",probe,"--out",run1,"--overlap-threshold","0.3")
            candidates=json.loads((run1/"orphan-candidates.json").read_text())["candidates"]
            self.assertTrue(any(x["url"].endswith("/orphan") for x in candidates))
            self.run_cli("build","--source",ROOT/"fixtures/source","--out",run2)
            comparison=json.loads(self.run_cli("compare",run1,run2).stdout); self.assertTrue(comparison["changes"])
            self.assertTrue(any(x["type"].startswith("EDGE_") for x in comparison["changes"]))

    def test_doctor_and_invalid_input(self):
        self.assertTrue(json.loads(self.run_cli("doctor").stdout)["ok"])
        self.run_cli("build",expected=1)
        self.run_cli("build","--source",ROOT/"fixtures/source","--min-similarity","2",expected=1)

    def test_malformed_inputs_path_fuzz_and_read_only_boundary(self):
        source = ROOT / "fixtures" / "source"
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob("*") if p.is_file()}
        rng = random.Random(20260811)
        values = ["", "/definitely/not/here"]
        values.extend("".join(rng.choice("%[]:/?@\\abc") for _ in range(20)) for _ in range(50))
        for value in values:
            result = self.run_cli("build", "--source", value, expected=1)
            self.assertNotIn("Traceback", result.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"; root.mkdir()
            (root / "bad.html").write_text("<html><title>broken<script>{not json", encoding="utf-8")
            (root / "bad.json").write_text('{"unterminated":', encoding="utf-8")
            self.run_cli("build", "--source", root, "--out", Path(tmp) / "run")
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob("*") if p.is_file()})

    def test_deterministic_rerun_cache_invalidation_and_budgets(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "first", Path(tmp) / "second"
            for run in (first, second): self.run_cli("build", "--source", ROOT / "fixtures/source", "--out", run, "--deterministic")
            for name in ("graph.json", "nodes.jsonl", "edges.jsonl", "clusters.json", "overlaps.json", "orphan-candidates.json", "link-opportunities.json", "metadata.json", "report.md"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)
            self.run_cli("build", "--source", ROOT / "fixtures/source", "--out", first, expected=1)
            tiny = Path(tmp) / "tiny"
            self.run_cli("build", "--source", ROOT / "fixtures/source", "--out", tiny, "--max-output-bytes", "1024", expected=1)
            self.assertFalse(tiny.exists(), "budget failure must not leave a partial run")
            self.run_cli("build", "--source", ROOT / "fixtures/source", "--max-nodes", "0", expected=1)

    def test_portable_ids_input_and_candidate_budgets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); left = root / "left"; right = root / "right"
            shutil.copytree(ROOT / "fixtures/source", left); shutil.copytree(ROOT / "fixtures/source", right)
            run_left, run_right = root / "run-left", root / "run-right"
            self.run_cli("build", "--source", left, "--out", run_left, "--deterministic")
            self.run_cli("build", "--source", right, "--out", run_right, "--deterministic")
            self.assertEqual((run_left / "nodes.jsonl").read_bytes(), (run_right / "nodes.jsonl").read_bytes())
            self.assertTrue(all(not Path(n["source_path"]).is_absolute() for n in map(json.loads, (run_left / "nodes.jsonl").read_text().splitlines())))
            budgeted = root / "budgeted"; budgeted.mkdir(); (budgeted / "large.md").write_text("word " * 400, encoding="utf-8")
            self.run_cli("build", "--source", budgeted, "--out", root / "input-limited", "--max-input-bytes", "1024", expected=1)
            dense = root / "dense"; dense.mkdir()
            for index in range(20): (dense / f"{index}.md").write_text("# Shared\n\ncommon terms across every page", encoding="utf-8")
            limited = root / "pair-limited"
            self.run_cli("build", "--source", dense, "--out", limited, "--max-candidate-pairs", "10", expected=1)
            self.assertFalse(limited.exists())

    def test_scale_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"; source.mkdir()
            for index in range(300):
                (source / f"page-{index:04d}.md").write_text(f"# Page {index}\n\nshared topic group {index % 20} unique-{index}", encoding="utf-8")
            started = time.monotonic(); run = Path(tmp) / "run"
            self.run_cli("build", "--source", source, "--out", run, "--max-nodes", "300")
            self.assertLess(time.monotonic() - started, 60)
            metadata = json.loads((run / "metadata.json").read_text())
            self.assertEqual(300, metadata["counts"]["nodes"])
            self.assertEqual(300, metadata["budgets"]["max_nodes"])


if __name__=="__main__": unittest.main(verbosity=2)
