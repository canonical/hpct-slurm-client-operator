#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""HPC Team SLURM client charm."""

import logging

from hpctlib.misc import service_forced_update
from hpctlib.ops.charm.service import ServiceCharm
from ops.charm import InstallEvent, StartEvent, StopEvent
from ops.framework import StoredState
from ops.main import main

from manager import MungeManager, SlurmClientManager

logger = logging.getLogger(__name__)


class SlurmClientCharm(ServiceCharm):
    """Slurm client charm. Encapsulates slurmd and munge."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.slurm_client_manager = SlurmClientManager()
        self.munge_manager = MungeManager()

    @service_forced_update()
    def _service_install(self, event: InstallEvent) -> None:
        """Fired when charm is first deployed."""
        self.service_set_state("waiting")
        self.service_set_status_message("Installing munge")
        self.service_update_status()
        self.munge_manager.install()

        self.service_set_status_message("Installing slurmd")
        self.service_update_status()
        self.slurm_client_manager.install()

        self.service_set_state("started")
        self.service_set_status_message()
        self.service_update_status()

    @service_forced_update()
    def _service_start(self, event: StartEvent) -> None:
        """Fired when service-start is run."""
        self.service_set_state("idle")
        self.service_set_status_message("Starting munge")
        self.service_update_status()
        self.munge_manager.start()

        self.service_set_status_message("Starting slurmd")
        self.service_update_status()
        self.slurm_client_manager.start()

        self.service_set_state("started")
        self.service_set_status_message()
        self.service_update_status()

    @service_forced_update()
    def _service_stop(self, event: StopEvent, force: bool) -> None:
        """Fired when service-stop is run."""
        self.service_set_state("idle")
        self.service_set_status_message("Stopping slurmctld")
        self.service_update_status()
        self.slurm_client_manager.stop()

        self.service_set_status_message("Stopping munge")
        self.service_update_status()
        self.munge_manager.stop()

        self.service_set_state("broken")
        self.service_set_status_message("Slurm server is not active.")
        self.service_update_status()


if __name__ == "__main__":
    main(SlurmClientCharm)
