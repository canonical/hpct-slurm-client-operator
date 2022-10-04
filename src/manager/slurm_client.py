#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage slurmd."""

import hashlib
import ipaddress
import logging
import os

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


class SlurmdNotFoundError(Exception):
    """Raised when trying to perform an operation with slurmd but slurmd is not installed."""

    def __init__(self, name: str, desc: str = "Slurmd is not installed.") -> None:
        self.name = name
        self.desc = desc
        super().__init__(self.desc)

    def __str__(self) -> str:
        """String representation of SlurmdNotFoundError."""
        return f"{self.desc} Please install slurmd using {self.name}.install()."


class SlurmConfNotFoundError(Exception):
    """Raised when manager cannot locate the `slurm.conf` file on a unit."""

    def __init__(self, path: str, desc: str = "slurm.conf not found on host.") -> None:
        self.path = path
        self.desc = desc
        super().__init__(self.desc)

    def __str__(self) -> str:
        """String representation of SlurmConfNotFoundError."""
        return f"{self.desc} Location searched: {self.path}"


class SlurmClientManager:
    """Top-level manager class for controlling slurmctld on unit."""

    def __init__(self) -> None:
        self.__memory = Memory()
        self.__memory.convert("mb", floor=True)
        self.__network = Network()

    @property
    def installed(self) -> bool:
        """Installation status of slurmd.

        Returns:
            bool: True if slurmd is installed on unit;
            False if slurmd is not installed on unit.
        """
        return self.__is_installed()

    @property
    def running(self) -> bool:
        """Status of slurmd daemon.

        Returns:
            bool: True if slurmd daemon is running;
            False if slurmd daemon is not running.
        """
        return service_running("slurmd")

    @property
    def cpu_count(self) -> int:
        """Retrieve unit's total CPUs.

        Returns:
            int: Unit's total CPUs.
        """
        return os.cpu_count()

    @property
    def free_memory(self) -> int:
        """Retrieve the unit's free memory in mebibytes.

        Returns:
            int: Unit's free memory in mebibytes.
        """
        return self.__memory.memavailable

    @property
    def hostname(self) -> str:
        """Retrieve hostname of unit.

        Returns:
            str: Hostname of unit.
        """
        return self.__network.info["hostname"]

    @property
    def ipv4_address(self) -> ipaddress.IPv4Address:
        """Retrieve IPv4 address of unit's eth0 interface.

        Returns:
            ipaddress.IPv4Address: IPv4 address of unit's eth0 interface.
        """
        for iface in self.__network.info["ifaces"]:
            if iface["name"] == "eth0":
                for addr in iface["info"]["addr_info"]:
                    if addr["family"] == "inet":
                        return addr["address"]

    @property
    def hash(self) -> bool:
        """sha224 hash of `slurm.conf`.

        Raises:
            SlurmConfNotFoundError: Thrown if `/etc/slurm/slurm.conf` does not exist on unit.

        Returns:
            str: sha224 hash of `slurm.conf`.
        """
        if os.path.isfile("/etc/slurm/slurm.conf"):
            md5 = hashlib.md5()
            md5.update(open("/etc/munge/munge.key", "rb").read())
            return md5.hexdigest()
        else:
            raise SlurmConfNotFoundError("/etc/slurm/slurm.conf")

    @property
    def conf_file(self) -> str:
        """Location of slurm configuration file on unit.

        Raises:
            SlurmConfNotFoundError: Thrown if `/etc/slurm/slurm.conf` does not exist on unit.

        Returns:
            str: Path to slurm configuration file on unit.
        """
        if os.path.isfile("/etc/slurm/slurm.conf"):
            return "/etc/slurm/slurm.conf"
        else:
            raise SlurmConfNotFoundError("/etc/slurm/slurm.conf")

    def generate_dummy_conf(self) -> None:
        """Generate a dummy slurm configuration."""
        if os.path.isfile("/etc/slurm/slurm.conf"):
            os.remove("/etc/slurm/slurm.conf")
        open("/etc/slurm/slurm.conf", "w").close()

    def write_new_conf(self, conf: FileDataInterface) -> None:
        """Write a new slurm configuration to `/etc/slurm/slurm.conf`.

        Args:
            conf (FileDataInterface): `slurm.conf` file received from event app.

        Raises:
            SlurmdNotFoundError: Thrown if slurmd is not yet installed on unit.
        """
        if self.__is_installed():
            logger.debug("Stopping slurmd daemon to set new slurm.conf file.")
            self.stop()
            if os.path.isfile("/etc/slurm/slurm.conf"):
                os.remove("/etc/slurm/slurm.conf")
            conf.save(conf.path)
            logger.debug("New slurm.conf file set. Restarting slurmd daemon.")
            self.start()
        else:
            raise SlurmdNotFoundError(self.__class__.__name__)

    def install(self) -> None:
        """Install SLURM compute daemon."""
        try:
            logger.debug("Installing SLURM Compute Daemon (slurmd).")
            apt.add_package("slurmd")
        except apt.PackageNotFoundError:
            logger.error("Could not install slurmd. Not found in package cache.")
        except apt.PackageError as e:
            logger.error(f"Could not install slurmd. Reason: {e.message}.")
        finally:
            logger.debug("slurmd installed.")

    def start(self) -> None:
        """Start SLURM compute daemon."""
        if self.__is_installed():
            logger.debug("Starting slurmd service.")
            if not service_running("slurmd"):
                service_start("slurmd")
                logger.debug("slurmd service started.")
            else:
                logger.debug("slurmd service is already running.")
        else:
            raise SlurmdNotFoundError(self.__class__.__name__)

    def stop(self) -> None:
        """Stop SLURM compute daemon."""
        if self.__is_installed():
            logger.debug("Stopping slurmd service.")
            if service_running("slurmd"):
                service_stop("slurmd")
                logger.debug("slurmd service stopped.")
            else:
                logger.debug("slurmd service is already stopped.")
        else:
            raise SlurmdNotFoundError(self.__class__.__name__)

    def restart(self) -> None:
        """Restart SLURM compute daemon."""
        if self.__is_installed():
            logger.debug("Restarting slurmd service.")
            service_restart("slurmd")
            logger.debug("slurmd service restarted.")
        else:
            raise SlurmdNotFoundError(self.__class__.__name__)

    def __is_installed(self) -> bool:
        """Internal function to check if slurmd Debian package is installed on the unit.

        Returns:
            bool: True if Debian package is present; False if Debian package is not present.
        """
        try:
            slurmctld_status = apt.DebianPackage.from_installed_package("slurmd")
            if slurmctld_status.present:
                return True
            else:
                return False
        except apt.PackageNotFoundError:
            return False
