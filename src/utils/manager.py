#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage slurmd, munge, etc."""

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

    def install(self, knob: str) -> None:
        """Dispatch for installing charm dependencies.
        Args:
            knob (str): Install function to dispatch.
                Options:
                    "slurmd": SLURM compute daemon
        """
        self.cache = apt.Cache()
        dispatch = {"slurmd": self._install_slurmd}
        dispatch[knob]()

    def _install_slurmd(self) -> None:
        """Install SLURM compute daemon"""
        logger.debug("Installing SLURM Compute Daemon (slurmd)")
        slurmctld_pkg = self.cache["slurmd"]
        slurmctld_pkg.mark_install()
        self.cache.commit()
        logger.debug("slurmd installed.")

    def enable(self, knob: str) -> None:
        """Dispatch for enabling charmed services.
        Args:
            knob (str): Enable function to dispatch.
                Options:
                    "slurmd": SLURM compute daemon
        """
        dispatch = {"slurmd": self._enable_slurmd}
        dispatch[knob]()

    def _enable_slurmd(self) -> None:
        logger.debug("Enabling slurmd service.")
        self.systemd.EnableUnitFiles(["slurmd.service"], False, True)
        self.systemd.Reload()
        logger.debug("slurmd service enabled.")

    def start(self, knob: str) -> None:
        """Dispatch for starting charmed services.
        Args:
            knob (str): Enable function to dispatch.
                Options:
                    "slurmd": SLURM compute daemon
        """
        dispatch = {"slurmd": self._start_slurmd}
        dispatch[knob]()

    def _start_slurmd(self) -> None:
        logger.debug("Starting slurmd service.")
        self.systemd.StartUnit("slurmd.service", "fail")
        self.systemd.Reload()
        logger.debug("slurmd service started.")

    def stop(self, knob: str) -> None:
        """Dispatch for stopping charmed services.
        Args:
            knob (str): Enable function to dispatch.
                Options:
                    "slurmd": SLURM compute daemon
        """
        dispatch = {"slurmd": self._stop_slurmd}
        dispatch[knob]()

    def _stop_slurmd(self) -> None:
        logger.debug("Stopping slurmd service.")
        self.systemd.StopUnit("slurmd.service", "fail")
        self.systemd.Reload()
        logger.debug("slurmd service stopped.")
