# Interactive static demo

Regenerate the deterministic, offline demonstration directly with Kujo:

```bash
kujo run scripts/build-demo.kujo
```

Open `demo/index.html` locally. Its accessible filter is self-contained and its
Content Security Policy denies network access. Every displayed node, count, and
term links to the committed public-corpus artifact that supports it, plus the
Kujo generator or engine source. Byte-golden artifacts are verified on every
supported platform.
