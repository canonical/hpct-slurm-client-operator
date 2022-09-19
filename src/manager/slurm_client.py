#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage slurmd."""

import logging

import apt
import dbus


logger = logging.getLogger(__name__)


class SlurmClientManager:
    def __init__(self) -> None:
        _bus = dbus.SystemBus()
        _systemd = _bus.get_object(
            "org.freedesktop.systemd1", "/org/freedesktop/systemd1"
        )
        self.systemd = dbus.Interface(_systemd, "org.freedesktop.systemd1.Manager")

    def install(self) -> None:
        """Install SLURM compute daemon"""
        logger.debug("Installing SLURM Compute Daemon (slurmd)")
        cache = apt.Cache()
        slurmctld_pkg = cache["slurmd"]
        slurmctld_pkg.mark_install()
        cache.commit()
        logger.debug("slurmd installed.")

    def enable(self) -> None:
        logger.debug("Enabling slurmd service.")
        self.systemd.EnableUnitFiles(["slurmd.service"], False, True)
        self.systemd.Reload()
        logger.debug("slurmd service enabled.")

    def start(self) -> None:
        logger.debug("Starting slurmd service.")
        self.systemd.StartUnit("slurmd.service", "fail")
        self.systemd.Reload()
        logger.debug("slurmd service started.")

    def stop(self) -> None:
        logger.debug("Stopping slurmd service.")
        self.systemd.StopUnit("slurmd.service", "fail")
        self.systemd.Reload()
        logger.debug("slurmd service stopped.")
