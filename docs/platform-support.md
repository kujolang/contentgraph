# Platform support

| Platform | Support | Validation |
| --- | --- | --- |
| Linux x86_64 | Supported | GitHub Actions native validation, launcher, UTF-8 paths, GraphML |
| macOS arm64/x86_64 | Supported | GitHub Actions native validation, launcher, UTF-8 paths, GraphML |
| Windows x86_64 | Supported | GitHub Actions via Git Bash plus direct `.cmd` launcher validation, `.exe` runtime discovery, UTF-8 paths, GraphML |

ContentGraph 0.2 is qualified against Kujo 1.0.1 and supports Kujo 1.x. Python is not required. Filesystem
inputs must be UTF-8 or are read lossily by the source adapter; JSON contracts
remain strict UTF-8. Network access is never required at runtime.
