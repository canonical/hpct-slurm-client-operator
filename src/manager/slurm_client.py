#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Set up and manage slurmd."""

import logging

import charms.operator_libs_linux.v0.apt as apt
from charms.operator_libs_linux.v1.systemd import (
    service_restart,
    service_running,
    service_start,
    service_stop,
)

logger = logging.getLogger(__name__)


class SlurmClientManager:
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
        logger.debug("Starting slurmd service.")
        if not service_running("slurmd"):
            service_start("slurmd")
            logger.debug("slurmd service started.")
        else:
            logger.debug("slurmd service is already running.")

    def stop(self) -> None:
        """Stop SLURM compute daemon."""
        logger.debug("Stopping slurmd service.")
        if service_running("slurmd"):
            service_stop("slurmd")
            logger.debug("slurmd service stopped.")
        else:
            logger.debug("slurmd service is already stopped.")

    def restart(self) -> None:
        """Restart SLURM compute daemon."""
        logger.debug("Restarting slurmd service.")
        service_restart("slurmd")
        logger.debug("slurmd service restarted.")
