#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Tests for SlurmServerManager class."""

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
            "name": "test-slurm-client-manager",
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
            manager_file = open(os.getenv("SLURM_CLIENT_MANAGER")).read()
            instance.files.put("/root/slurm_client.py", manager_file)
            charm_include = os.getenv("CHARM_LIB_INCLUDE").split(":")
            for lib in charm_include:
                instance.files.recursive_put(lib, "/root/lib")

        func(*args, **kwargs)

    return wrapper


class TestSlurmServer:
    @remote
    def test_install(self) -> None:
        """Test install for slurmd."""
        result = self._run("install.py")
        assert int(result.exit_code) == 0

    @remote
    def test_start(self) -> None:
        """Test that slurmd service can start."""
        result = self._run("start.py")
        assert int(result.exit_code) == 0

    @remote
    def test_stop(self) -> None:
        """Test that slurmd service can stop."""
        result = self._run("stop.py")
        assert int(result.exit_code) == 0

    @remote
    def test_restart(self) -> None:
        """Test that slurmd service can restart."""
        result = self._run("restart.py")
        assert int(result.exit_code) == 0

    def _run(self, scriptlet: str) -> Tuple:
        """Execute python3 scriptlet inside the LXD test instance.

        Args:
            scriptlet (str): Scriptlet to execute inside instance.

        Returns:
            Tuple: Exit code, stdout, and stderr from scriptlet.
        """
        instance = Client().instances.get("test-slurm-client-manager")
        env = {"PYTHONPATH": "/root:/root/lib"}
        script = open(os.path.join(os.getenv("SCRIPTLETS_INCLUDE"), scriptlet)).read()
        instance.files.put(f"/tmp/{scriptlet}", script)
        return instance.execute(["python3", f"/tmp/{scriptlet}"], environment=env)
