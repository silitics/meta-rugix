set dotenv-load

KAS_VERSION := "4.7"

export KAS_WORK_DIR := env("KAS_WORK_DIR", justfile_directory() + "/_kas")
export KAS_BUILD_DIR := env("KAS_BUILD_DIR", justfile_directory() + "/build")
export SSTATE_DIR := env("SSTATE_DIR", justfile_directory() + "/cache/sstate-cache")
export DL_DIR := env("DL_DIR", justfile_directory() + "/cache/downloads")

[private]
_default:
    @just --list

init:
    #!/usr/bin/env bash
    set -euo pipefail
    python3 -m venv .venv
    . .venv/bin/activate
    pip3 install kas=={{KAS_VERSION}}
    mkdir -p "{{KAS_WORK_DIR}}"
    mkdir -p "{{KAS_BUILD_DIR}}"
    mkdir -p "{{SSTATE_DIR}}"
    mkdir -p "{{DL_DIR}}"

clean:
    rm -rf "{{KAS_WORK_DIR}}"
    rm -rf "{{KAS_BUILD_DIR}}"
    mkdir -p "{{KAS_WORK_DIR}}"
    mkdir -p "{{KAS_BUILD_DIR}}"

kas *args:
    @[ -d .venv ] || just install
    @.venv/bin/kas {{args}}

build *args:
    @.venv/bin/kas build {{args}}