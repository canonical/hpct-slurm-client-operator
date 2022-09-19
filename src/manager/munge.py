#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage munge."""

import logging

import apt
import dbus


logger = logging.getLogger(__name__)


class MungeManager:
    def __init__(self) -> None:
        _bus = dbus.SystemBus()
        _systemd = _bus.get_object(
            "org.freedesktop.systemd1", "/org/freedesktop/systemd1"
        )
        self.systemd = dbus.Interface(_systemd, "org.freedesktop.systemd1.Manager")

    def install(self) -> None:
        """Install munge."""
        logger.debug("Installing munge.")
        cache = apt.Cache()
        munge_pkg = cache["munge"]
        munge_pkg.mark_install()
        cache.commit()
        logger.debug("munge installed.")

    def enable(self) -> None:
        logger.debug("Enabling munge service.")
        self.systemd.EnableUnitFiles(["munge.service"], False, True)
        self.systemd.Reload()
        logger.debug("munge service enabled.")

    def start(self) -> None:
        logger.debug("Starting munge service.")
        self.systemd.StartUnit("munge.service", "fail")
        self.systemd.Reload()
        logger.debug("slurmd service started.")

    def stop(self) -> None:
        logger.debug("Stopping munge service.")
        self.systemd.StopUnit("munge.service", "fail")
        self.systemd.Reload()
        logger.debug("munge service stopped.")
