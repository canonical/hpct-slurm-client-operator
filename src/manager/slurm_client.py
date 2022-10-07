#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage slurmd."""

import grp
import hashlib
import logging
import os
import pathlib
import pwd
from typing import Union

import charms.operator_libs_linux.v0.apt as apt
from charms.operator_libs_linux.v1.systemd import (
    service_running,
    service_start,
    service_stop,
)
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

        self.conf_file_path = "/etc/slurm/slurm.conf"
        self.cpu_count = os.cpu_count()
        self.free_memory = self.__memory.memavailable
        self.hostname = self.__network.info["hostname"]
        for iface in self.__network.info["ifaces"]:
            if iface["name"] == "eth0":
                for addr in iface["info"]["addr_info"]:
                    if addr["family"] == "inet":
                        self.ipv4_address = addr["address"]

    def get_hash(self, path: Union[str, None] = None) -> Union[str, None]:
        """Get the sha224 hash of a file.

        Args:
            path (str | None): Path to file to hash.
            Defaults to `self.conf_file_path` if path is None.

        Returns:
            str: sha224 hash of the file, or None if file does not exist.
        """
        path = self.conf_file_path if path is None else path
        return (
            hashlib.sha224(open(path, "rb").read()).hexdigest() if os.path.isfile(path) else None
        )

    def write_new_conf(
        self,
        data: bytes,
        path: Union[str, None] = None,
        mode: Union[int, None] = None,
        user: Union[str, None] = None,
        group: Union[str, None] = None,
    ) -> None:
        """Write a new slurm configuration.

        Args:
            data (bytes): Slurm configuration file.
            path (str | None): Path to write configuration file. Defaults to self.conf_file_path.
            mode (int | None): File access mode. Defaults to None.
            user (str | None): User to own file. Defaults to None.
            group (str | None): Group to own file. Defaults to None.

        Raises:
            SlurmClientManagerError: Thrown if slurmd is not installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping slurmd daemon to set new slurm.conf file.")
            self.stop()
            path = self.conf_file_path if path is None else path
            p = pathlib.Path(path)
            p.touch()
            uid = pwd.getpwnam(user).pw_uid if user is not None else user
            gid = grp.getgrnam(group).gr_gid if group is not None else group
            if -1 not in [uid, gid] and None not in [uid, gid]:
                os.chown(path, uid, gid)
            if mode is not None:
                p.chmod(mode)
            p.write_bytes(data)
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
        except apt.PackageError or apt.PackageNotFoundError as e:
            logger.error(f"Error installing slurmd. Reason: {e.message}.")
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
            self.stop()
            self.start()
            logger.debug("slurmd service restarted.")
        else:
            raise SlurmClientManagerError("slurmd is not installed.")

    def __is_installed(self) -> bool:
        """Internal function to check if slurmd Debian package is installed on the unit.

        Returns:
            bool: True if Debian package is present; False if Debian package is not present.
        """
        return True if apt.DebianPackage.from_installed_package("slurmd").present else False
