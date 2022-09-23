#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Configurations for MungeManager tests."""

from pylxd import Client


def pytest_unconfigure(config) -> None:
    """Teardown LXD test instance."""
    instance = Client().instances.get("test-munge-manager")
    instance.stop(wait=True)
    instance.delete(wait=True)
