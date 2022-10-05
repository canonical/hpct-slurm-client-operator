#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage slurmd."""

import hashlib
import logging
import os
from typing import Union

import charms.operator_libs_linux.v0.apt as apt
from charms.operator_libs_linux.v1.systemd import (
    service_restart,
    service_running,
    service_start,
    service_stop,
)
from hpctinterfaces.ext.file import FileDataInterface
from sysprober.memory import Memory
from sysprober.network import Network

logger = logging.getLogger(__name__)


class SlurmClientManagerError(Exception):
    """Raised when the slurm client manager encounters an error."""

    ...


class SlurmClientManager:
    """Top-level manager class for controlling slurmctld on unit."""

    def __init__(self) -> None:
        self.__memory = Memory()
        self.__memory.convert("mb", floor=True)
        self.__network = Network()

        self.conf_file = "/etc/slurm/slurm.conf"
        self.cpu_count = os.cpu_count()
        self.free_memory = self.__memory.memavailable
        self.hostname = self.__network.info["hostname"]
        for iface in self.__network.info["ifaces"]:
            if iface["name"] == "eth0":
                for addr in iface["info"]["addr_info"]:
                    if addr["family"] == "inet":
                        self.ipv4_address = addr["address"]

    def get_hash(self, file: Union[str, None] = None) -> Union[str, None]:
        """Get the sha224 hash of a file.

        Args:
            str | None: File to hash. Defaults to self.conf_file if file is None.

        Returns:
            str: sha224 hash of the file, or None if file does not exist.
        """
        file = self.conf_file if file is None else file
        return (
            hashlib.sha224(open(file, "rb").read()).hexdigest() if os.path.isfile(file) else None
        )

    def write_new_conf(self, conf: FileDataInterface) -> None:
        """Write a new slurm configuration.

        Args:
            conf (FileDataInterface): `slurm.conf` file received from event app.

        Raises:
            SlurmClientManagerError: Thrown if slurmd is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping slurmd daemon to set new slurm.conf file.")
            self.stop()
            conf.save(conf.path)
            logger.debug("New slurm.conf file set. Restarting slurmd daemon.")
            self.start()
        else:
            raise SlurmClientManagerError("slurmd is not installed.")

    def install(self) -> None:
        """Install slurm compute daemon.

        Raises:
            SlurmClientManagerError: Thrown if slurmd fails to install.
        """
        try:
            logger.debug("Installing slurm compute daemon (slurmd).")
            apt.add_package("slurmd")
        except apt.PackageNotFoundError:
            logger.error("Could not install slurmd. Not found in package cache.")
            raise SlurmClientManagerError("Failed to install slurmd.")
        except apt.PackageError as e:
            logger.error(f"Could not install slurmd. Reason: {e.message}.")
            raise SlurmClientManagerError("Failed to install slurmd.")
        finally:
            logger.debug("slurmd installed.")

    def start(self) -> None:
        """Start slurm compute daemon.

        Raises:
            SlurmClientManagerError: Thrown if slurmd is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Starting slurmd service.")
            if not service_running("slurmd"):
                service_start("slurmd")
                logger.debug("slurmd service started.")
            else:
                logger.debug("slurmd service is already running.")
        else:
            raise SlurmClientManagerError("slurmd is not installed.")

    def stop(self) -> None:
        """Stop slurm compute daemon.

        Raises:
            SlurmClientManagerError: Thrown if slurmd is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping slurmd service.")
            if service_running("slurmd"):
                service_stop("slurmd")
                logger.debug("slurmd service stopped.")
            else:
                logger.debug("slurmd service is already stopped.")
        else:
            raise SlurmClientManagerError("slurmd is not installed.")

    def restart(self) -> None:
        """Restart slurm compute daemon.

        Raises:
            SlurmClientManagerError: Thrown if slurmd is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Restarting slurmd service.")
            service_restart("slurmd")
            logger.debug("slurmd service restarted.")
        else:
            raise SlurmClientManagerError("slurmd is not installed.")

    def __is_installed(self) -> bool:
        """Internal function to check if slurmd Debian package is installed on the unit.

        Returns:
            bool: True if Debian package is present; False if Debian package is not present.
        """
        return True if apt.DebianPackage.from_installed_package("slurmd").present else False
