#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(); p.add_argument("--nodes",type=int,default=1000); args=p.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        source=Path(tmp)/"source"; source.mkdir()
        for i in range(args.nodes): (source/f"page-{i:05d}.md").write_text(f"# Page {i}\n\nshared topic {i%50} unique-{i}\n",encoding="utf-8")
        out=Path(tmp)/"run"; started=time.monotonic(); subprocess.run(["python3",str(ROOT/"bridge/contentgraph.py"),"build","--source",str(source),"--out",str(out),"--max-nodes",str(args.nodes),"--deterministic"],capture_output=True,check=True)
        size=sum(x.stat().st_size for x in out.iterdir() if x.is_file())
        print(json.dumps({"schema":"contentgraph.benchmark/v1","nodes":args.nodes,"seconds":round(time.monotonic()-started,3),"output_bytes":size},sort_keys=True))
if __name__=="__main__": main()
