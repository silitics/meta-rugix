"""Tests for explicit Rugix bundle recipes."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from conftest import PROJECT_ROOT


_BITBAKE_TARGET_RE = re.compile(r"^[A-Za-z0-9_.+-]+$")

_EXPLICIT_BUNDLE_RECIPES = [
    pytest.param(
        "examples/qemu-x86_64-grub.yaml",
        "qemux86-64",
        "update-bundle-minimal",
        id="qemu-x86_64-grub",
    ),
    pytest.param(
        "examples/qemu-arm64-uboot.yaml",
        "qemuarm64",
        "update-bundle-minimal",
        id="qemu-arm64-uboot",
    ),
    pytest.param(
        "examples/raspberrypi-tryboot.yaml",
        "raspberrypi-armv8",
        "update-bundle-minimal",
        id="raspberrypi-tryboot",
    ),
    pytest.param(
        "examples/raspberrypi-uboot.yaml",
        "raspberrypi-armv8",
        "update-bundle-minimal",
        id="raspberrypi-uboot",
    ),
]


@pytest.mark.build
@pytest.mark.timeout(7200)
@pytest.mark.parametrize(("kas_config", "machine", "bundle_recipe"), _EXPLICIT_BUNDLE_RECIPES)
def test_explicit_bundle_recipe_builds(
    kas_config: str, machine: str, bundle_recipe: str
):
    """Build a bundle recipe directly, without relying on image build side effects."""
    if not shutil.which("kas-container"):
        pytest.skip("kas-container not installed")

    if not _BITBAKE_TARGET_RE.fullmatch(bundle_recipe):
        pytest.fail(f"Invalid bundle recipe name: {bundle_recipe!r}")

    env = os.environ.copy()
    build_dir = Path(env.get("KAS_BUILD_DIR", PROJECT_ROOT / "build"))
    build_dir = build_dir / "tests" / "explicit-bundle-recipes" / Path(kas_config).stem
    work_dir = Path(env.get("KAS_WORK_DIR", PROJECT_ROOT / "_kas"))

    build_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    env["KAS_BUILD_DIR"] = str(build_dir)
    env["KAS_WORK_DIR"] = str(work_dir)

    subprocess.run(
        ["kas-container", "checkout", kas_config],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )

    partitions_dir = build_dir / "tmp/deploy/images" / machine / "partitions"
    shutil.rmtree(partitions_dir, ignore_errors=True)

    subprocess.run(
        ["kas-container", "shell", kas_config, "-c", f"bitbake {bundle_recipe}"],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )
