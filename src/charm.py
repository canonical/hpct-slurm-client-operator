#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""HPC Team SLURM client charm."""

import logging

from hpctinterfaces import interface_registry
from hpctops.charm.service import ServiceCharm
from hpctops.misc import service_forced_update
from ops.charm import (
    InstallEvent,
    RelationChangedEvent,
    RelationJoinedEvent,
    StartEvent,
    StopEvent,
)
from ops.main import main

from interface import (
    AuthMungeInterface,
    SlurmComputeInterface,
    SlurmControllerInterface,
)
from manager import MungeManager, SlurmClientManager

logger = logging.getLogger(__name__)


class SlurmClientCharm(ServiceCharm):
    """Slurm client charm. Encapsulates slurmd and munge."""

    def __init__(self, *args) -> None:
        super().__init__(*args)

        self.slurm_client_manager = SlurmClientManager()
        self.munge_manager = MungeManager()

        self.auth_munge_interface = interface_registry.load(
            "relation-auth-munge", self, "auth-munge"
        )
        self.slurm_compute_interface = interface_registry.load(
            "relation-slurm-compute", self, "slurm-compute"
        )
        self.slurm_controller_interface = interface_registry.load(
            "relation-slurm-controller", self, "slurm-controller"
        )

        self.framework.observe(
            self.on.auth_munge_relation_changed, self._auth_munge_relation_changed
        )
        self.framework.observe(
            self.on.slurm_compute_relation_joined, self._slurm_compute_relation_joined
        )
        self.framework.observe(
            self.on.slurm_controller_relation_changed, self._slurm_controller_relation_changed
        )

    @service_forced_update()
    def _service_install(self, event: InstallEvent) -> None:
        """Fired when charm is first deployed."""
        self.service_set_status_message("Installing munge")
        self.service_update_status()
        self.munge_manager.install()

        self.service_set_status_message("Installing slurmd")
        self.service_update_status()
        self.slurm_client_manager.install()

        self.service_set_status_message()
        self.service_update_status()

    @service_forced_update()
    def _service_start(self, event: StartEvent) -> None:
        """Fired when service-start is run."""
        self.service_set_status_message("Starting munge")
        self.service_update_status()
        self.munge_manager.start()

        self.service_set_status_message("Starting slurmd")
        self.service_update_status()
        self.slurm_client_manager.start()

        self.service_set_status_message()
        self.service_update_status()

    @service_forced_update()
    def _service_stop(self, event: StopEvent, force: bool) -> None:
        """Fired when service-stop is run."""
        self.service_set_status_message("Stopping slurmd")
        self.service_update_status()
        self.slurm_client_manager.stop()

        self.service_set_status_message("Stopping munge")
        self.service_update_status()
        self.munge_manager.stop()

        self.service_set_status_message("Slurm client is not active.")
        self.service_update_status()

    @service_forced_update()
    def _auth_munge_relation_changed(self, event: RelationChangedEvent) -> None:
        """Fired when new `munge.key` is loaded into `event.app` relation data bucket."""
        self.service_set_status_message("New munge key detected")
        self.service_update_status()
        i = self.auth_munge_interface.select(event.app)

        if i.nonce == "":
            self.service_set_status_message("Munge key is not ready")
            self.service_update_status()
        elif self.munge_manager.hash != i.munge_key.checksum:
            self.munge_manager.write_new_key(i.munge_key)
            self.service_set_status_message("Munge key updated")
            self.service_update_status()
        else:
            self.service_set_status_message("Munge does not need to be updated")
            self.service_update_status()

    @service_forced_update()
    def _slurm_compute_relation_joined(self, event: RelationJoinedEvent) -> None:
        """Fired when new SLURM controller is related to application."""
        pass

    @service_forced_update()
    def _slurm_controller_relation_changed(self, event: RelationChangedEvent) -> None:
        """Fired when new `slurm.conf` file is loaded into `event.app` relation data bucket."""
        pass


if __name__ == "__main__":
    interface_registry.register("relation-auth-munge", AuthMungeInterface)
    interface_registry.register("relation-slurm-compute", SlurmComputeInterface)
    interface_registry.register("relation-slurm-controller", SlurmControllerInterface)
    main(SlurmClientCharm)
