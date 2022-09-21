#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage munge."""

import logging

import charms.operator_libs_linux.v0.apt as apt
from charms.operator_libs_linux.v1.systemd import (
    service_restart,
    service_running,
    service_start,
    service_stop,
)

logger = logging.getLogger(__name__)


class MungeManager:
    """Top-level manager class for controlling munge on unit."""

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
        logger.debug("Starting munge service.")
        if not service_running("munge"):
            service_start("munge")
            logger.debug("munnge service started.")
        else:
            logger.debug("munge service is already running.")

    def stop(self) -> None:
        """Stop MUNGE daemon."""
        logger.debug("Stopping munge service.")
        if service_running("munge"):
            service_stop("munge")
            logger.debug("munge service stopped.")
        else:
            logger.debug("munge service is already stopped.")

    def restart(self) -> None:
        """Restart MUNGE daemon."""
        logger.debug("Restarting munge service.")
        service_restart("munge")
        logger.debug("munge service restarted.")
