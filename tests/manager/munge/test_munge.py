#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Tests for MungeManager class."""

import os
from functools import wraps
from typing import Any, Tuple

from pylxd import Client


def remote(func: Any) -> None:
    """Decorator for setting up LXD test instance."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        client = Client()
        config = {
            "name": "test-munge-manager",
            "source": {
                "type": "image",
                "mode": "pull",
                "server": "https://images.linuxcontainers.org",
                "protocol": "simplestreams",
                "alias": "ubuntu/jammy",
            },
            "project": "default",
        }

        if not client.instances.exists(config["name"]):
            instance = client.instances.create(config, wait=True)
            instance.start(wait=True)
            manager_file = open(os.getenv("MUNGE_MANAGER")).read()
            instance.files.put("/root/munge.py", manager_file)
            charm_include = os.getenv("CHARM_LIB_INCLUDE").split(":")
            for lib in charm_include:
                instance.files.recursive_put(lib, "/root/lib")

        func(*args, **kwargs)

    return wrapper


class TestMungeManager:
    @remote
    def test_install(self) -> None:
        """Test install for munge."""
        result = self._run("install.py")
        assert int(result.exit_code) == 0

    @remote
    def test_start(self) -> None:
        """Test that munge service can start."""
        result = self._run("start.py")
        assert int(result.exit_code) == 0

    @remote
    def test_stop(self) -> None:
        """Test that munge service can stop."""
        result = self._run("stop.py")
        assert int(result.exit_code) == 0

    @remote
    def test_restart(self) -> None:
        """Test that munge service can restart."""
        result = self._run("restart.py")
        assert int(result.exit_code) == 0

    def _run(self, scriptlet: str) -> Tuple:
        """Execute python3 scriptlet inside the LXD test instance.

        Args:
            scriptlet (str): Scriptlet to execute inside instance.

        Returns:
            Tuple: Exit code, stdout, and stderr from scriptlet.
        """
        instance = Client().instances.get("test-munge-manager")
        env = {"PYTHONPATH": "/root:/root/lib"}
        script = open(os.path.join(os.getenv("SCRIPTLETS_INCLUDE"), scriptlet)).read()
        instance.files.put(f"/tmp/{scriptlet}", script)
        return instance.execute(["python3", f"/tmp/{scriptlet}"], environment=env)
