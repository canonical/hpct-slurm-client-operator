#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage munge."""

import grp
import hashlib
import logging
import os
import pathlib
import pwd
import subprocess
from typing import Union

import charms.operator_libs_linux.v0.apt as apt
from charms.operator_libs_linux.v1.systemd import (
    service_running,
    service_start,
    service_stop,
)

logger = logging.getLogger(__name__)


class MungeManagerError(Exception):
    """Raised when the munge manager encounters an error."""

    ...


class MungeManager:
    """Top-level manager class for controlling munge on unit."""

    def __init__(self) -> None:
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
            MungeManagerError: Thrown if munge is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping munge daemon to generate new key.")
            self.stop()
            os.remove(self.key_file_path) if os.path.isfile(self.key_file_path) else ...
            subprocess.run(["mungekey", "-c", "-k", self.key_file_path])
            self.start()
            logger.debug("New munge key generated. Restarting munge daemon")
        else:
            raise MungeManagerError("Munge is not installed.")

    def write_new_key(
        self,
        data: bytes,
        mode: int,
        user: str,
        group: str,
        path: Union[str, None] = None,
    ) -> None:
        """Write a new munge key.

        Args:
            data (bytes): Munge key file.
            mode (int | None): File access mode. Defaults to None.
            user (str | None) : User to own file. Defaults to None.
            group (str | None): Group to own file. Defaults to None.
            path (str | None): Path to write configuration file. Defaults to self.key_file_path.

        Raises:
            MungeManagerError: Thrown if munge is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping munge daemon to set new munge key.")
            self.stop()
            path = self.key_file_path if path is None else path
            p = pathlib.Path(path)
            p.touch()
            uid = pwd.getpwnam(user).pw_uid
            gid = grp.getgrnam(group).gr_gid
            os.chown(path, uid, gid)
            p.chmod(mode)
            p.write_bytes(data)
            logger.debug("New munge key set. Restarting munge daemon.")
            self.start()
        else:
            raise MungeManagerError("Munge is not installed.")

    def install(self) -> None:
        """Install munge on unit.

        Raises:
            MungeManagerError: Thrown if munge fails to install.
        """
        try:
            logger.debug("Installing munge authentication daemon (munge).")
            apt.add_package("munge")
        except apt.PackageError or apt.PackageNotFoundError as e:
            logger.error(f"Error installing munge. Reason: {e.message}.")
            raise MungeManagerError("Failed to install munge.")
        finally:
            logger.debug("Munge installed.")

    def start(self) -> None:
        """Start munge daemon.

        Raises:
            MungeManagerError: Thrown if munge is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Starting munge service.")
            if not service_running("munge"):
                service_start("munge")
                logger.debug("Munge service started.")
            else:
                logger.debug("Munge service is already running.")
        else:
            raise MungeManagerError("Munge is not installed.")

    def stop(self) -> None:
        """Stop munge daemon.

        Raises:
            MungeManagerError: Thrown if munge is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping munge service.")
            if service_running("munge"):
                service_stop("munge")
                logger.debug("Munge service stopped.")
            else:
                logger.debug("Munge service is already stopped.")
        else:
            raise MungeManagerError("Munge is not installed.")

    def restart(self) -> None:
        """Restart munge daemon.

        Raises:
            MungeManagerError: Thrown if munge is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Restarting munge service.")
            self.stop()
            self.start()
            logger.debug("Munge service restarted.")
        else:
            raise MungeManagerError("Munge is not installed.")

    def __is_installed(self) -> bool:
        """Internal function to check in munge Debian package is installed on the unit.

        Returns:
            bool: True if Debian package is present; False if Debian package is not present.
        """
        return True if apt.DebianPackage.from_installed_package("munge").present else False
