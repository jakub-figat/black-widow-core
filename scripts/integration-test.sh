#!/usr/bin/env sh

set -e
set -u


coverage run --source=src -m pytest tests/integration