#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage munge."""

import logging
import os
import subprocess

import charms.operator_libs_linux.v0.apt as apt
from charms.operator_libs_linux.v1.systemd import (
    service_restart,
    service_running,
    service_start,
    service_stop,
)
from hpctlib.ext.interfaces.file import FileDataInterface

logger = logging.getLogger(__name__)


class MungeNotFoundError(Exception):
    """Raised when trying to perform an operation with munge but munge is not installed."""

    def __init__(self, name: str, desc: str = "Munge is not installed.") -> None:
        self.name = name
        self.desc = desc
        super().__init__(self.desc)

    def __repr__(self) -> str:
        """String representation of MungeNotFoundError."""
        return f"{self.desc} Please install munge using {self.name}.install()."


class MungeKeyNotFoundError(Exception):
    """Raised when manager can not locate munge.key file on a unit."""

    def __init__(self, path: str, desc: str = "Munge key not found on host.") -> None:
        self.path = path
        self.desc = desc
        super().__init__(self.desc)

    def __repr__(self) -> str:
        """String representation of MungeKeyNotFoundError."""
        return f"{self.desc} Location searched: {self.path}"


class MungeManager:
    """Top-level manager class for controlling munge on unit."""

    @property
    def key(self) -> str:
        """Location of munge key file on unit.

        Raises:
            MungeKeyNotFoundError: Thrown if `/etc/munge/munge.key` does not exist on unit.

        Returns:
            str: Path to munge key file on unit
        """
        if os.path.isfile("/etc/munge/munge.key"):
            return "/etc/munge/munge.key"
        else:
            raise MungeKeyNotFoundError("/etc/munge/munge.key")

    @property
    def installed(self) -> bool:
        """Installation status of munge.

        Returns:
            bool: True if munge is installed on unit; False if munge is not installed on unit
        """
        return self.__is_installed()

    def generate_new_key(self) -> None:
        """Generate a new munge.key file using `mungekey` utility.

        Raises:
            MungeNotFoundError: Thrown if munge is not yet installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping munge daemon to generate new key.")
            self.stop()
            if os.path.isfile("/etc/munge/munge.key"):
                os.remove("/etc/munge/munge.key")
            subprocess.run(["mungekey", "-c"])
            self.start()
            logger.debug("New munge key generated. Restarting munge daemon")
        else:
            raise MungeNotFoundError(self.__class__.__name__)

    def write_new_key(self, key: FileDataInterface) -> None:
        """Write a new munge key to `/etc/munge/munge.key`.

        Args:
            key (FileDataInterface): `munge.key` file received from event app

        Raises:
            MungeNotFoundError: Thrown if munge is not yet installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping munge daemon to set new munge key.")
            self.stop()
            if os.path.isfile("/etc/munge/munge.key"):
                os.remove("/etc/munge/munge.key")
            key.save(key.path)
            logger.debug("New munge key set. Restarting munge daemon.")
            self.start()
        else:
            raise MungeNotFoundError(self.__class__.__name__)

    def install(self) -> None:
        """Install MUNGE."""
        try:
            logger.debug("Installing MUNGE authentication daemon (munge).")
            apt.add_package("munge")
        except apt.PackageNotFoundError:
            logger.error("Could not install munge. Not found in package cache.")
        except apt.PackageError as e:
            logger.error(f"Could not install munge. Reason: {e.message}.")
        finally:
            logger.debug("munge installed.")

    def start(self) -> None:
        """Start MUNGE daemon."""
        if self.__is_installed():
            logger.debug("Starting munge service.")
            if not service_running("munge"):
                service_start("munge")
                logger.debug("munge service started.")
            else:
                logger.debug("munge service is already running.")
        else:
            raise MungeNotFoundError(self.__class__.__name__)

    def stop(self) -> None:
        """Stop MUNGE daemon."""
        if self.__is_installed():
            logger.debug("Stopping munge service.")
            if service_running("munge"):
                service_stop("munge")
                logger.debug("munge service stopped.")
            else:
                logger.debug("munge service is already stopped.")
        else:
            raise MungeNotFoundError(self.__class__.__name__)

    def restart(self) -> None:
        """Restart MUNGE daemon."""
        if self.__is_installed():
            logger.debug("Restarting munge service.")
            service_restart("munge")
            logger.debug("munge service restarted.")
        else:
            raise MungeNotFoundError(self.__class__.__name__)

    def __is_installed(self) -> bool:
        """Internal function to check in munge Debian package is installed on the unit.

        Returns:
            bool: True if Debian package is present; False if Debian package is not present.
        """
        try:
            munge_status = apt.DebianPackage.from_installed_package("munge")
            if munge_status.present:
                return True
            else:
                return False
        except apt.PackageNotFoundError:
            return False
