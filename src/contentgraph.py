#!/usr/bin/env python3
"""Deterministic local content-network bridge for ContentGraph."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit

VERSION = "0.1.0"
METHOD = "deterministic-lexical/v1"
MAX_FILE = 5 * 1024 * 1024
MAX_NODES = 20_000
MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_CANDIDATE_PAIRS = 2_000_000
DETERMINISTIC_TIME = "1970-01-01T00:00:00Z"
DETERMINISTIC = False
EXCLUDED = {".git", ".contentgraph", ".siteprobe", ".webops", "node_modules", "vendor", "kennel_packages", "output", "dist", "build", "__pycache__"}
STOP = {"a","an","and","are","as","at","be","by","for","from","has","have","in","is","it","its","of","on","or","that","the","their","this","to","was","were","will","with","you","your","we","our","can","not","use","using","into","than","then","when","where","what","which","who","how"}


def now() -> str:
    if DETERMINISTIC: return DETERMINISTIC_TIME
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def render_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(identity: str) -> str:
    return "CG-" + hashlib.sha256(identity.strip().lower().encode()).hexdigest()[:20]


def fingerprint(text: str) -> str:
    return hashlib.sha256(re.sub(r"\s+", " ", text).strip().lower().encode()).hexdigest()


def tokens(text: str) -> list[str]:
    return [x for x in re.findall(r"[a-z0-9][a-z0-9_-]{1,}", text.lower()) if x not in STOP and not x.isdigit()]


def strip_markup(text: str) -> str:
    text = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"[#>*_`\[\](){}|]", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"): return {}, text
    end = text.find("\n---", 4)
    if end < 0: return {}, text
    values = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1); values[key.strip()] = value.strip().strip('"\'')
    return values, text[end + 4:]


class InputBudget:
    def __init__(self, maximum: int):
        self.maximum = maximum
        self.used = 0

    def consume(self, path: Path, enforce_file_limit: bool = True) -> None:
        size = path.stat().st_size
        if enforce_file_limit and size > MAX_FILE:
            raise RuntimeError(f"input file exceeds {MAX_FILE} byte limit: {path.name}")
        self.used += size
        if self.used > self.maximum:
            raise RuntimeError(f"input budget exceeded ({self.used} > {self.maximum} bytes)")


def source_files(root: Path, budget: InputBudget) -> Iterable[Path]:
    resolved = root.resolve()
    if resolved.is_file():
        yield resolved; return
    for path in sorted(resolved.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".markdown", ".html", ".htm", ".txt", ".json"}: continue
        if any(part in EXCLUDED for part in path.parts): continue
        try:
            actual = path.resolve(); actual.relative_to(resolved)
        except (OSError, ValueError): continue
        budget.consume(actual)
        yield actual


def title_from_text(path: Path, meta: dict[str, str], body: str) -> str:
    if meta.get("title"): return meta["title"]
    heading = re.search(r"^#\s+(.+)$", body, re.M)
    if heading: return heading.group(1).strip()
    html_title = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    if html_title: return strip_markup(html_title.group(1))
    return path.stem.replace("-", " ").replace("_", " ").title()


def ingest_source(path_value: str, budget: InputBudget, max_nodes: int = MAX_NODES) -> list[dict[str, Any]]:
    if not path_value.strip(): raise RuntimeError("source path must not be empty")
    root = Path(path_value).expanduser().resolve()
    if not root.exists(): raise RuntimeError(f"source path not found: {root}")
    nodes = []
    for path in source_files(root, budget):
        raw = path.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_frontmatter(raw); text = strip_markup(body)
        rel = str(path.relative_to(root)) if root.is_dir() else path.name
        identity = meta.get("canonical") or meta.get("url") or "source:" + Path(rel).as_posix()
        nodes.append({"schema":"contentgraph.node/v1","id":stable_id(identity),"url":meta.get("url", ""),"canonical_url":meta.get("canonical", meta.get("url", "")),"source_path":rel,"source_relative":rel,"title":title_from_text(path, meta, body),"content_type":meta.get("type", path.suffix.lstrip(".")),"text":text,"content_fingerprint":fingerprint(text),"cluster":"","parent_id":"","child_ids":[],"incoming_links":0,"outgoing_links":0,"related_pages":[],"search_queries":[],"portfolio_state":meta.get("portfolio_state", ""),"last_material_update":meta.get("last_updated", meta.get("date", "")),"crawl_depth":None,"sitemap_member":None,"existing_targets":[]})
        if len(nodes) > max_nodes: raise RuntimeError(f"node cap exceeded while reading source: {root}")
    return nodes


def ingest_siteprobe(run_value: str, budget: InputBudget, max_nodes: int = MAX_NODES) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    run = Path(run_value).expanduser().resolve()
    pages_path = run / "pages.jsonl"; links_path = run / "links.json"
    if not pages_path.is_file() or not links_path.is_file(): raise RuntimeError(f"invalid SiteProbe run: {run}")
    budget.consume(pages_path, False); budget.consume(links_path, False)
    nodes = []
    with pages_path.open(encoding="utf-8") as pages:
        for line in pages:
            if not line.strip(): continue
            page = json.loads(line); url = page.get("canonical") or page.get("final_url") or page["url"]
            title = page.get("title", "")
            headings = " ".join(" ".join(v) for v in page.get("headings", {}).values())
            metadata_text = " ".join([title, page.get("meta_description", ""), headings])
            # SiteProbe stores a primary-content fingerprint rather than full body text.
            nodes.append({"schema":"contentgraph.node/v1","id":stable_id(url),"url":page.get("final_url", url),"canonical_url":url,"source_path":"","source_relative":"","title":title,"content_type":page.get("content_type", ""),"text":metadata_text,"content_fingerprint":page.get("content_fingerprint") or fingerprint(metadata_text),"cluster":"","parent_id":"","child_ids":[],"incoming_links":page.get("incoming_link_count", 0),"outgoing_links":page.get("outgoing_link_count", 0),"related_pages":[],"search_queries":[],"portfolio_state":"","last_material_update":"","crawl_depth":page.get("depth"),"sitemap_member":page.get("sitemap_member"),"existing_targets":[x.get("url") for x in page.get("internal_links", [])]})
            if len(nodes) > max_nodes: raise RuntimeError(f"node cap exceeded while reading SiteProbe run: {run}")
    url_to_id = {n["url"]: n["id"] for n in nodes}; url_to_id.update({n["canonical_url"]: n["id"] for n in nodes})
    edges = []
    for link in load(links_path).get("links", []):
        if link.get("internal") and link.get("source") in url_to_id and link.get("target") in url_to_id:
            edges.append({"schema":"contentgraph.edge/v1","source":url_to_id[link["source"]],"target":url_to_id[link["target"]],"type":"internal-link","method":"existing-internal-link","weight":1.0,"evidence":{"anchor":link.get("text", ""),"source_url":link["source"],"target_url":link["target"]}})
    return nodes, edges


def merge_nodes(groups: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for nodes in groups:
        for node in nodes:
            identity = (node.get("canonical_url") or node.get("url") or node.get("source_path") or node["id"]).lower()
            key = stable_id(identity)
            if key not in merged: merged[key] = node; merged[key]["id"] = key
            else:
                current = merged[key]
                for field in ("url","canonical_url","source_path","source_relative","title","content_type","text","last_material_update","portfolio_state"):
                    if not current.get(field) and node.get(field): current[field] = node[field]
                current["existing_targets"] = sorted(set(current.get("existing_targets", []) + node.get("existing_targets", [])))
    return sorted(merged.values(), key=lambda n: n["id"])


def vectors(nodes: list[dict[str, Any]]) -> tuple[dict[str, dict[str, float]], dict[str, list[str]]]:
    docs = {n["id"]: tokens(" ".join([n.get("title", ""), n.get("title", ""), n.get("text", "")])) for n in nodes}
    df = Counter(term for terms in docs.values() for term in set(terms)); total = max(1, len(nodes)); result = {}; signals = {}
    for node_id, terms in docs.items():
        counts = Counter(terms); weights = {term: (1 + math.log(count)) * (math.log((1 + total) / (1 + df[term])) + 1) for term, count in counts.items()}
        norm = math.sqrt(sum(v*v for v in weights.values())) or 1.0
        result[node_id] = {term: value / norm for term, value in weights.items()}
        signals[node_id] = [x[0] for x in sorted(weights.items(), key=lambda x: (-x[1], x[0]))[:12]]
    return result, signals


def candidate_scores(vecs: dict[str, dict[str, float]], maximum: int) -> dict[tuple[str, str], float]:
    """Accumulate exact sparse cosine scores without scanning disjoint documents."""
    postings: defaultdict[str, list[tuple[str, float]]] = defaultdict(list)
    for node_id, vector in vecs.items():
        for term, weight in vector.items(): postings[term].append((node_id, weight))
    scores: defaultdict[tuple[str, str], float] = defaultdict(float)
    for term in sorted(postings):
        entries = sorted(postings[term])
        for index, (left, left_weight) in enumerate(entries):
            for right, right_weight in entries[index + 1:]:
                pair = (left, right)
                if pair not in scores and len(scores) >= maximum:
                    raise RuntimeError(f"candidate-pair budget exceeded ({maximum}); raise --max-candidate-pairs or narrow the corpus")
                scores[pair] += left_weight * right_weight
    return scores


class UnionFind:
    def __init__(self, ids: list[str]): self.parent = {x:x for x in ids}
    def find(self, x: str) -> str:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]; x = self.parent[x]
        return x
    def union(self, a: str, b: str) -> None:
        a, b = self.find(a), self.find(b)
        if a != b: self.parent[max(a,b)] = min(a,b)


def search_associations(paths: list[str], nodes: list[dict[str, Any]], budget: InputBudget) -> list[dict[str, Any]]:
    url_map = {n.get("url"): n for n in nodes if n.get("url")}; url_map.update({n.get("canonical_url"): n for n in nodes if n.get("canonical_url")})
    edges = []
    for value in paths:
        path = Path(value).expanduser().resolve()
        if not path.is_file(): raise RuntimeError(f"SearchBridge result not found: {path}")
        budget.consume(path, False)
        data = load(path)
        if data.get("schema") != "searchbridge.result/v1": raise RuntimeError(f"invalid SearchBridge result: {value}")
        if data.get("capability") != "search.performance": continue
        for row in data.get("rows", []):
            node = url_map.get(row.get("page")); query = row.get("query")
            if node and query:
                node["search_queries"].append({"query":query,"clicks":row.get("clicks"),"impressions":row.get("impressions"),"position":row.get("position"),"provider":data.get("provider"),"retrieved_at":data.get("retrieved_at")})
                edges.append({"schema":"contentgraph.edge/v1","source":"query:"+hashlib.sha256(query.encode()).hexdigest()[:16],"target":node["id"],"type":"search-query-association","method":"measured-provider-evidence","weight":float(row.get("impressions") or 0),"evidence":{"query":query,"provider":data.get("provider")}})
    return edges


def build(args: argparse.Namespace) -> int:
    if not args.siteprobe and not args.source: raise RuntimeError("build requires --siteprobe or --source")
    budget = InputBudget(args.max_input_bytes); groups = []; existing_edges = []
    for value in args.siteprobe:
        nodes, edges = ingest_siteprobe(value, budget, args.max_nodes); groups.append(nodes); existing_edges.extend(edges)
    for value in args.source: groups.append(ingest_source(value, budget, args.max_nodes))
    nodes = merge_nodes(groups)
    if len(nodes) > args.max_nodes: raise RuntimeError("node cap exceeded")
    vecs, signals = vectors(nodes); node_by_id = {n["id"]: n for n in nodes}; ids = sorted(node_by_id); similarities = []
    uf = UnionFind(ids)
    scores = candidate_scores(vecs, args.max_candidate_pairs); qualified: defaultdict[str, list[tuple[float, str]]] = defaultdict(list)
    for (left, right), score in sorted(scores.items()):
        if score >= args.min_similarity:
            qualified[left].append((score, right)); qualified[right].append((score, left))
            if score >= args.cluster_threshold: uf.union(left, right)
    retained: set[tuple[str, str]] = set()
    for node_id, candidates in qualified.items():
        for _, other_id in sorted(candidates, key=lambda item: (-item[0], item[1]))[:args.max_related_per_node]:
            retained.add(tuple(sorted((node_id, other_id))))
    similarities = [{"source":left,"target":right,"score":round(scores[(left,right)],6)} for left, right in sorted(retained)]
    components: defaultdict[str, list[str]] = defaultdict(list)
    for node_id in ids: components[uf.find(node_id)].append(node_id)
    clusters = []
    for index, member_ids in enumerate(sorted(components.values(), key=lambda x: (-len(x), x[0])), 1):
        cluster_id = f"cluster-{index:03d}"; terms = Counter(term for node_id in member_ids for term in signals[node_id][:8])
        label_terms = [x[0] for x in terms.most_common(4)]
        clusters.append({"id":cluster_id,"label":" / ".join(label_terms) or "unclassified","node_ids":member_ids,"size":len(member_ids),"method":METHOD})
        for node_id in member_ids: node_by_id[node_id]["cluster"] = cluster_id
    similarity_edges = [{"schema":"contentgraph.edge/v1","source":x["source"],"target":x["target"],"type":"lexical-similarity","method":METHOD,"weight":x["score"],"evidence":{"shared_terms":sorted(set(signals[x["source"]]) & set(signals[x["target"]]))[:12]}} for x in similarities]
    search_edges = search_associations(args.searchbridge, nodes, budget)
    edges = sorted(existing_edges + similarity_edges + search_edges, key=lambda e: (e["type"], e["source"], e["target"]))
    incoming = Counter(e["target"] for e in existing_edges); outgoing = Counter(e["source"] for e in existing_edges)
    related: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in similarities:
        related[item["source"]].append({"node_id":item["target"],"score":item["score"],"method":METHOD})
        related[item["target"]].append({"node_id":item["source"],"score":item["score"],"method":METHOD})
    for node in nodes:
        node["incoming_links"] = max(node.get("incoming_links") or 0, incoming[node["id"]]); node["outgoing_links"] = max(node.get("outgoing_links") or 0, outgoing[node["id"]]); node["topic_signals"] = signals[node["id"]]; node["related_pages"] = sorted(related[node["id"]], key=lambda x: (-x["score"], x["node_id"]))[:20]; node.pop("text", None); node.pop("existing_targets", None)
    overlaps = [{"id":"overlap-"+hashlib.sha256((x["source"]+x["target"]).encode()).hexdigest()[:16],"left":x["source"],"right":x["target"],"score":x["score"],"classification":"cannibalization-candidate","method":METHOD,"requires_intent_review":True} for x in similarities if x["score"] >= args.overlap_threshold]
    existing_pairs = {(e["source"],e["target"]) for e in existing_edges}
    opportunities = []
    for item in similarities:
        for source, target in ((item["source"], item["target"]), (item["target"], item["source"])):
            if (source, target) not in existing_pairs:
                opportunities.append({"id":"link-"+hashlib.sha256((source+target).encode()).hexdigest()[:16],"source":source,"target":target,"score":item["score"],"method":METHOD,"reason":"lexically related and not currently linked in this direction","requires_context_review":True})
    orphans = [{"node_id":n["id"],"url":n.get("url"),"title":n["title"],"incoming_links":n["incoming_links"],"classification":"orphan" if n["incoming_links"] == 0 else "weakly-connected"} for n in nodes if n["incoming_links"] <= 1]
    run_id = "deterministic" if args.deterministic else (Path(args.out).name if args.out else datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    out = Path(args.out or f".contentgraph/{run_id}").expanduser().resolve()
    if out.exists(): raise RuntimeError(f"output path already exists: {out}")
    graph = {"schema":"contentgraph.graph/v1","run_id":run_id,"generated_at":now(),"method":METHOD,"nodes":[n["id"] for n in nodes],"edges":[{"source":e["source"],"target":e["target"],"type":e["type"],"weight":e["weight"]} for e in edges]}
    metadata = {"schema":"contentgraph.metadata/v1","run_id":run_id,"inputs":{"siteprobe":args.siteprobe,"source":args.source,"searchbridge":args.searchbridge},"thresholds":{"minimum":args.min_similarity,"cluster":args.cluster_threshold,"overlap":args.overlap_threshold},"budgets":{"max_nodes":args.max_nodes,"max_input_bytes":args.max_input_bytes,"max_output_bytes":args.max_output_bytes,"max_report_tokens":args.max_report_tokens,"max_candidate_pairs":args.max_candidate_pairs,"max_related_per_node":args.max_related_per_node},"usage":{"input_bytes":budget.used,"candidate_pairs":len(scores),"retained_similarity_pairs":len(similarities)},"counts":{"nodes":len(nodes),"edges":len(edges),"clusters":len(clusters),"overlaps":len(overlaps),"orphans":len(orphans),"link_opportunities":len(opportunities)}}
    report = ["# ContentGraph Report","",f"Run: {run_id}","","## Attention","",f"- Orphan or weak candidates: {len(orphans)}",f"- High-overlap candidates requiring intent review: {len(overlaps)}",f"- Contextual link opportunities requiring review: {len(opportunities)}","","## Coverage","",f"- Content nodes: {len(nodes)}",f"- Relationship edges: {len(edges)}",f"- Topic clusters: {len(clusters)}","",f"Method: `{METHOD}`. Full evidence remains in the run directory.",f"Report budget: {args.max_report_tokens} approximate tokens.",""]
    artifacts = {
        "graph.json": render_json(graph),
        "nodes.jsonl": "".join(json.dumps(n,sort_keys=True)+"\n" for n in nodes),
        "edges.jsonl": "".join(json.dumps(e,sort_keys=True)+"\n" for e in edges),
        "clusters.json": render_json({"schema":"contentgraph.clusters/v1","clusters":clusters}),
        "overlaps.json": render_json({"schema":"contentgraph.overlaps/v1","overlaps":overlaps}),
        "orphan-candidates.json": render_json({"schema":"contentgraph.orphans/v1","candidates":orphans}),
        "link-opportunities.json": render_json({"schema":"contentgraph.link-opportunities/v1","opportunities":opportunities}),
        "metadata.json": render_json(metadata),
        "report.md": "\n".join(report),
    }
    output_bytes = sum(len(value.encode("utf-8")) for value in artifacts.values())
    if output_bytes > args.max_output_bytes: raise RuntimeError(f"output budget exceeded ({output_bytes} > {args.max_output_bytes} bytes)")
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}.tmp-", dir=out.parent))
    try:
        for name, value in artifacts.items(): (staging/name).write_text(value, encoding="utf-8")
        staging.rename(out)
    finally:
        if staging.exists(): shutil.rmtree(staging)
    print(json.dumps({"run":str(out),"counts":metadata["counts"]},sort_keys=True) if args.json else f"ContentGraph build complete: {out}\nNodes: {len(nodes)}  Edges: {len(edges)}")
    return 0


def validate_run(run: Path) -> None:
    required = ["graph.json","nodes.jsonl","edges.jsonl","clusters.json","overlaps.json","orphan-candidates.json","link-opportunities.json","metadata.json","report.md"]
    missing = [x for x in required if not (run/x).is_file()]
    if missing: raise RuntimeError("invalid ContentGraph run, missing: " + ", ".join(missing))
    if load(run/"graph.json").get("schema") != "contentgraph.graph/v1": raise RuntimeError("unsupported graph schema")


def jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def compare(old: Path, new: Path) -> dict[str, Any]:
    validate_run(old); validate_run(new); before={n["id"]:n for n in jsonl(old/"nodes.jsonl")}; after={n["id"]:n for n in jsonl(new/"nodes.jsonl")}; changes=[]
    for x in sorted(after.keys()-before.keys()): changes.append({"type":"NODE_ADDED","node_id":x})
    for x in sorted(before.keys()-after.keys()): changes.append({"type":"NODE_REMOVED","node_id":x})
    for x in sorted(before.keys()&after.keys()):
        if before[x]["content_fingerprint"] != after[x]["content_fingerprint"]: changes.append({"type":"CONTENT_CHANGED","node_id":x})
        if before[x]["cluster"] != after[x]["cluster"]: changes.append({"type":"CLUSTER_CHANGED","node_id":x,"before":before[x]["cluster"],"after":after[x]["cluster"]})
        if before[x]["incoming_links"] != after[x]["incoming_links"]: changes.append({"type":"INCOMING_LINKS_CHANGED","node_id":x,"before":before[x]["incoming_links"],"after":after[x]["incoming_links"]})
    before_edges = {(e["source"], e["target"], e["type"]): e for e in jsonl(old/"edges.jsonl")}
    after_edges = {(e["source"], e["target"], e["type"]): e for e in jsonl(new/"edges.jsonl")}
    for source, target, edge_type in sorted(after_edges.keys() - before_edges.keys()): changes.append({"type":"EDGE_ADDED","source":source,"target":target,"edge_type":edge_type})
    for source, target, edge_type in sorted(before_edges.keys() - after_edges.keys()): changes.append({"type":"EDGE_REMOVED","source":source,"target":target,"edge_type":edge_type})
    for key in sorted(before_edges.keys() & after_edges.keys()):
        if before_edges[key].get("weight") != after_edges[key].get("weight"):
            changes.append({"type":"EDGE_WEIGHT_CHANGED","source":key[0],"target":key[1],"edge_type":key[2],"before":before_edges[key].get("weight"),"after":after_edges[key].get("weight")})
    return {"schema":"contentgraph.comparison/v1","old_run":str(old),"new_run":str(new),"changes":changes}


def export_graph(run: Path, fmt: str) -> str:
    if fmt == "json": return (run/"graph.json").read_text(encoding="utf-8")
    nodes=jsonl(run/"nodes.jsonl"); edges=jsonl(run/"edges.jsonl"); lines=['<?xml version="1.0" encoding="UTF-8"?>','<graphml xmlns="http://graphml.graphdrawing.org/xmlns">','<key id="title" for="node" attr.name="title" attr.type="string"/>','<key id="type" for="edge" attr.name="type" attr.type="string"/>','<graph edgedefault="directed">']
    lines.extend(f'<node id="{html.escape(n["id"])}"><data key="title">{html.escape(n["title"])}</data></node>' for n in nodes)
    lines.extend(f'<edge source="{html.escape(e["source"])}" target="{html.escape(e["target"])}"><data key="type">{html.escape(e["type"])}</data></edge>' for e in edges if not e["source"].startswith("query:"))
    lines.append("</graph></graphml>"); return "\n".join(lines)+"\n"


def parser() -> argparse.ArgumentParser:
    root=argparse.ArgumentParser(prog="contentgraph"); sub=root.add_subparsers(dest="command",required=True); sub.add_parser("doctor"); sub.add_parser("version")
    p=sub.add_parser("build"); p.add_argument("--siteprobe",action="append",default=[]); p.add_argument("--source",action="append",default=[]); p.add_argument("--searchbridge",action="append",default=[]); p.add_argument("--out"); p.add_argument("--min-similarity",type=float,default=0.12); p.add_argument("--cluster-threshold",type=float,default=0.20); p.add_argument("--overlap-threshold",type=float,default=0.55); p.add_argument("--max-nodes",type=int,default=5000); p.add_argument("--max-input-bytes",type=int,default=MAX_INPUT_BYTES); p.add_argument("--max-output-bytes",type=int,default=256 * 1024 * 1024); p.add_argument("--max-report-tokens",type=int,default=2000); p.add_argument("--max-candidate-pairs",type=int,default=MAX_CANDIDATE_PAIRS); p.add_argument("--max-related-per-node",type=int,default=20); p.add_argument("--deterministic",action="store_true"); p.add_argument("--json",action="store_true")
    p=sub.add_parser("inspect"); p.add_argument("run"); p.add_argument("--node",required=True)
    p=sub.add_parser("related"); p.add_argument("run"); p.add_argument("--node",required=True); p.add_argument("--limit",type=int,default=10)
    for name in ("orphans","clusters","overlaps","link-opportunities"):
        p=sub.add_parser(name); p.add_argument("run")
    p=sub.add_parser("compare"); p.add_argument("old"); p.add_argument("new")
    p=sub.add_parser("export"); p.add_argument("run"); p.add_argument("--format",choices=["json","graphml"],default="json"); p.add_argument("--out"); p.add_argument("--force",action="store_true")
    return root


def main() -> int:
    global DETERMINISTIC
    args=parser().parse_args()
    try:
        if args.command=="version": print(json.dumps({"name":"contentgraph","version":VERSION,"contract":"contentgraph.graph/v1","method":METHOD})); return 0
        if args.command=="doctor": print(json.dumps({"ok":True,"network_required":False,"paid_api_required":False,"method":METHOD,"max_nodes":MAX_NODES},sort_keys=True)); return 0
        if args.command=="build":
            DETERMINISTIC = args.deterministic
            for x in (args.min_similarity,args.cluster_threshold,args.overlap_threshold):
                if x<0 or x>1: raise RuntimeError("similarity thresholds must be between 0 and 1")
            if args.max_nodes < 1 or args.max_nodes > MAX_NODES: raise RuntimeError(f"--max-nodes must be between 1 and {MAX_NODES}")
            if args.max_input_bytes < 1024 or args.max_output_bytes < 1024 or args.max_report_tokens < 64 or args.max_candidate_pairs < 1 or args.max_related_per_node < 1 or args.max_related_per_node > 1000: raise RuntimeError("resource budgets are outside safe limits")
            return build(args)
        if args.command=="compare": print(json.dumps(compare(Path(args.old).resolve(),Path(args.new).resolve()),indent=2,sort_keys=True)); return 0
        run=Path(args.run).resolve(); validate_run(run)
        if args.command=="export":
            text=export_graph(run,args.format)
            if args.out:
                destination = Path(args.out).expanduser().resolve()
                if destination.exists() and not args.force: raise RuntimeError(f"export destination exists (use --force): {destination}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(text,encoding="utf-8")
            else: print(text,end="")
            return 0
        nodes=jsonl(run/"nodes.jsonl"); node_map={n["id"]:n for n in nodes}; node_map.update({n.get("url"):n for n in nodes if n.get("url")}); node_map.update({n.get("source_relative"):n for n in nodes if n.get("source_relative")})
        if args.command=="inspect":
            node=node_map.get(args.node)
            if not node: raise RuntimeError(f"node not found: {args.node}")
            relations=[e for e in jsonl(run/"edges.jsonl") if node["id"] in {e["source"],e["target"]}]; print(json.dumps({"node":node,"relationships":relations},indent=2,sort_keys=True)); return 0
        if args.command=="related":
            node=node_map.get(args.node)
            if not node: raise RuntimeError(f"node not found: {args.node}")
            if args.limit < 1 or args.limit > 1000: raise RuntimeError("--limit must be between 1 and 1000")
            print(json.dumps({"node_id":node["id"],"related":node["related_pages"][:args.limit]},indent=2,sort_keys=True)); return 0
        filename={"orphans":"orphan-candidates.json","clusters":"clusters.json","overlaps":"overlaps.json","link-opportunities":"link-opportunities.json"}[args.command]; print((run/filename).read_text(encoding="utf-8"),end=""); return 0
    except (RuntimeError,OSError,ValueError,KeyError,TypeError,UnicodeError,json.JSONDecodeError) as exc: print(f"ContentGraph: {str(exc)[:300]}",file=sys.stderr); return 1


if __name__=="__main__": raise SystemExit(main())
