#!/usr/bin/env sh

set -u
set -e

coverage run --source=src -m pytest tests/unit
