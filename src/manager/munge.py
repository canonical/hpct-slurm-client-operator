#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage munge."""

import hashlib
import logging
import os
import subprocess
from typing import Union

from hpctmanagers import ManagerException
from hpctmanagers.ubuntu import UbuntuManager

logger = logging.getLogger(__name__)


class MungeManager(UbuntuManager):
    """Top-level manager class for controlling munge on unit."""

    install_packages = ["munge"]
    systemd_services = ["munge"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.key_file_path = "/etc/munge/munge.key"

    def get_hash(self, path: Union[str, None] = None) -> Union[str, None]:
        """Get the sha224 hash of a file.

        Args:
            path (str | None): Path to file on unit.
            Defaults to `self.key_file_path` if path is None.

        Returns:
            str | None: sha224 hash of the file, or None if file does not exist.
        """
        path = self.key_file_path if path is None else path
        return (
            hashlib.sha224(open(path, "rb").read()).hexdigest() if os.path.isfile(path) else None
        )

    def generate_new_key(self) -> None:
        """Generate a new munge.key file using `mungekey` utility.

        Raises:
            ManagerException: Thrown if munge is not installed on unit.
        """
        if self.is_installed():
            logger.debug("Stopping munge daemon to generate new key.")
            self.stop()
            os.remove(self.key_file_path) if os.path.isfile(self.key_file_path) else ...
            subprocess.run(["mungekey", "-c", "-k", self.key_file_path])
            self.start()
            logger.debug("New munge key generated. Restarting munge daemon")
        else:
            raise ManagerException("Munge is not installed.")

    def restart(self) -> None:
        """Restart munge daemon.

        Raises:
            ManagerException: Thrown if munge is not installed on unit.
        """
        if self.is_installed():
            logger.debug("Restarting munge service.")
            self.stop() if self.is_running() else ...
            self.start() if not self.is_running() else ...
            logger.debug("Munge service restarted.")
        else:
            raise ManagerException("Munge is not installed.")
