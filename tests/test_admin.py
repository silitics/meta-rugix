"""Tests for the Rugix Admin example integration."""

import json

import pytest

from rugix_testkit import VMHandle


def test_admin_and_daemon_services(vm: VMHandle):
    """Verify the daemon and browser interface start and communicate."""
    for service in ("rugix-ctrl-daemon.service", "rugix-admin.service"):
        result = vm.run(
            ["systemctl", "is-active", service], check=False, hide=True
        )
        if result.stdout.strip() != "active":
            status = vm.run(
                ["systemctl", "status", "--no-pager", "--full", service],
                check=False,
                hide=True,
            )
            journal = vm.run(
                ["journalctl", "-u", service, "--no-pager", "-n", "100"],
                check=False,
                hide=True,
            )
            pytest.fail(f"{status.stdout}\n{status.stderr}\n{journal.stdout}")

    result = vm.run(
        ["wget", "-qO-", "http://127.0.0.1:7492/api/daemon"], hide=True
    )
    assert json.loads(result.stdout)["dangerouslyInsecure"] is False
