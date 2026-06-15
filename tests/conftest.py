"""Shared pytest fixtures for Rugix VM integration tests."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Generator
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread

import pytest

from rugix_testkit import Drive, Pflash, RugixCtrl, VMConfig, VMHandle

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_PLATFORMS: dict[str, tuple[str, Callable[[Path], VMConfig]]] = {
    "qemux86-64": ("tmp/deploy/images/qemux86-64", lambda d: _x86_64_config(d)),
    "qemuarm64": ("tmp/deploy/images/qemuarm64", lambda d: _arm64_config(d)),
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--test-outputs-dir",
        default="test-outputs",
        help="Directory for test artifacts (default: test-outputs/)",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "x86_64: x86_64/GRUB-specific tests")
    config.addinivalue_line("markers", "arm64: ARM64/U-Boot-specific tests")
    config.addinivalue_line("markers", "build: Yocto build tests")
    config.addinivalue_line("markers", "slow: long-running tests")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    build = Path(os.environ.get("KAS_BUILD_DIR", PROJECT_ROOT / "build"))
    available = _available_platforms(build) if build.is_dir() else set()
    for item in items:
        if hasattr(item, "callspec") and "platform" in item.callspec.params:
            if item.callspec.params["platform"] not in available:
                item.add_marker(pytest.mark.skip(reason="WIC image not built"))


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    report = yield
    if report.when == "call":
        _dump_test_artifacts(item)
    return report


@pytest.fixture(scope="session")
def build_dir() -> Path:
    path = Path(os.environ.get("KAS_BUILD_DIR", PROJECT_ROOT / "build"))
    assert path.is_dir(), f"Build directory not found: {path}"
    return path


@pytest.fixture(scope="session")
def http_server(build_dir: Path) -> Generator[HTTPServer]:
    handler = partial(_QuietHandler, directory=str(build_dir / "tmp/deploy/images"))
    server = HTTPServer(("0.0.0.0", 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    logger.info("HTTP server on port %d", server.server_port)
    yield server
    server.shutdown()


@pytest.fixture(params=list(_PLATFORMS.keys()))
def platform(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def vm(
    platform: str, build_dir: Path, request: pytest.FixtureRequest
) -> Generator[VMHandle]:
    subdir, factory = _PLATFORMS[platform]
    config = factory(build_dir / subdir)
    with VMHandle.start(config) as handle:
        request.node._vm_handle = handle  # type: ignore[attr-defined]
        yield handle


@pytest.fixture
def rugix(vm: VMHandle) -> RugixCtrl:
    return RugixCtrl(vm)


@pytest.fixture
def bundle_url(platform: str, http_server: HTTPServer) -> str:
    port = http_server.server_port
    return (
        f"http://10.0.2.2:{port}/{platform}/core-image-minimal-{platform}.rootfs.rugixb"
    )


def _dump_test_artifacts(item: pytest.Item) -> None:
    vm_handle: VMHandle | None = getattr(item, "_vm_handle", None)
    if vm_handle is None:
        return

    outputs_dir = Path(item.config.getoption("--test-outputs-dir"))
    safe_name = item.nodeid.replace("::", "--").replace("/", "--")
    artifact_dir = outputs_dir / safe_name
    artifact_dir.mkdir(parents=True, exist_ok=True)

    serial = vm_handle.serial_output
    if serial:
        (artifact_dir / "serial.log").write_text(serial)

    history = vm_handle.command_history
    if history:
        (artifact_dir / "commands.log").write_text(
            "\n\n".join(str(cmd) for cmd in history) + "\n"
        )


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        logger.debug("http: " + format, *args)


def _x86_64_config(deploy: Path) -> VMConfig:
    return VMConfig(
        arch="x86_64",
        drives=[
            Drive(
                file=deploy / "core-image-minimal-qemux86-64.rootfs.wic",
                overlay=True,
                size="16G",
            ),
        ],
        pflash=[
            Pflash(file=deploy / "ovmf.code.qcow2", format="qcow2", readonly=True),
            Pflash(file=deploy / "ovmf.vars.qcow2", format="qcow2"),
        ],
    )


def _arm64_config(deploy: Path) -> VMConfig:
    return VMConfig(
        arch="aarch64",
        cpu="cortex-a57",
        drives=[
            Drive(
                file=deploy / "core-image-minimal-qemuarm64.rootfs.wic",
                interface="virtio",
                overlay=True,
                size="16G",
            ),
        ],
        pflash=[
            Pflash(file=deploy / "u-boot.bin", size="64M", readonly=True),
            Pflash(size="64M"),
        ],
    )


def _available_platforms(build_dir: Path) -> set[str]:
    available = set()
    for name, (subdir, factory) in _PLATFORMS.items():
        deploy = build_dir / subdir
        try:
            cfg = factory(deploy)
            if all(d.file.exists() for d in cfg.drives):
                available.add(name)
        except Exception:
            pass
    return available
