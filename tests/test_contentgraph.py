#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/"bridge"/"contentgraph.py"


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
            self.run_cli("related",run,"--node",nodes[0]["id"])

    def test_siteprobe_ingestion_orphans_and_compare(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); probe=root/"probe"; self.siteprobe_fixture(probe); run1=root/"one"; run2=root/"two"
            self.run_cli("build","--siteprobe",probe,"--out",run1,"--overlap-threshold","0.3")
            candidates=json.loads((run1/"orphan-candidates.json").read_text())["candidates"]
            self.assertTrue(any(x["url"].endswith("/orphan") for x in candidates))
            self.run_cli("build","--source",ROOT/"fixtures/source","--out",run2)
            comparison=json.loads(self.run_cli("compare",run1,run2).stdout); self.assertTrue(comparison["changes"])

    def test_doctor_and_invalid_input(self):
        self.assertTrue(json.loads(self.run_cli("doctor").stdout)["ok"])
        self.run_cli("build",expected=1)
        self.run_cli("build","--source",ROOT/"fixtures/source","--min-similarity","2",expected=1)


if __name__=="__main__": unittest.main(verbosity=2)
