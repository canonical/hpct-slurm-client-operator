#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""HPC Team SLURM client charm."""

import logging

from hpctlib.ops.charm.service import ServiceCharm
from ops.charm import ActionEvent, InstallEvent, StartEvent, StopEvent
from ops.framework import StoredState
from ops.main import main

from manager import MungeManager, SlurmClientManager

logger = logging.getLogger(__name__)


class SlurmClientCharm(ServiceCharm):

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.auth_start_action, self._auth_start)
        self.framework.observe(self.on.auth_stop_action, self._auth_stop)

        self.manager = SlurmClientManager()
        self.auth_manager = MungeManager()

    def _auth_start(self, event: ActionEvent) -> None:
        """Fired when auth-start is run."""
        self.auth_manager.start()

    def _auth_stop(self, event: ActionEvent) -> None:
        """Fired when auth-stop is run."""
        self.auth_manager.stop()

    def _service_install(self, event: InstallEvent) -> None:
        "Fired when charm is first deployed."
        self.auth_manager.install()
        self.manager.install()

    def _service_start(self, event: StartEvent) -> None:
        """Fired when service-start is run."""
        self.manager.start()

    def _service_stop(self, event: StopEvent, force: bool) -> None:
        """Fired when service-stop is run."""
        self.manager.stop()


if __name__ == "__main__":
    main(SlurmClientCharm)
