#!/usr/bin/env bash
set -euo pipefail
git diff --check -- . ':(exclude).loop-engineering'
