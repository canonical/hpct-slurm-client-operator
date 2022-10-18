#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage slurmd."""

import hashlib
import logging
import os
from typing import Union

from hpctmanagers import ManagerException
from hpctmanagers.ubuntu import UbuntuManager
from sysprober.memory import Memory
from sysprober.network import Network

logger = logging.getLogger(__name__)


class SlurmClientManager(UbuntuManager):
    """Top-level manager class for controlling slurmctld on unit."""

    install_packages = ["slurmd"]
    systemd_services = ["slurmd"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
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

    def restart(self) -> None:
        """Restart slurm compute daemon.

        Raises:
            ManagerException: Thrown if slurmd is not installed on unit.
        """
        if self.is_installed():
            logger.debug("Restarting slurmd service.")
            self.stop()
            self.start()
            logger.debug("slurmd service restarted.")
        else:
            raise ManagerException("slurmd is not installed.")
