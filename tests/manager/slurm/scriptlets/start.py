#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Scriptlet to test start is working."""

import sys

import charms.operator_libs_linux.v0.apt as apt
from charms.operator_libs_linux.v1.systemd import service_running
from slurm_client import SlurmClientManager


def test() -> None:
    # Check slurmd is installed.
    if not _is_slurmd_installed():
        sys.exit(1)

    # Start slurmd.
    manager = SlurmClientManager()
    manager.start()

    # Check that service is active.
    if not service_running("slurmd"):
        sys.exit(1)
    else:
        sys.exit(0)


def _is_slurmd_installed() -> bool:
    try:
        apt.DebianPackage.from_installed_package("slurmd")
        return True
    except apt.PackageNotFoundError:
        return False


if __name__ == "__main__":
    test()
