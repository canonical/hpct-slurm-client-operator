#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface for the slurm-controller relation."""

from hpctlib.ext.interfaces.file import FileDataInterface
from hpctlib.interface.relation import AppBucketInterface, RelationSuperInterface
from hpctlib.interface.value import String


class SlurmControllerInterface(RelationSuperInterface):
    """Super interface for the slurm-controller relation."""

    def __init__(self, charm, relname: str, role=None) -> None:
        super().__init__(charm, relname, role)

        self.interface_classes[("provider", "app")] = self.SlurmControllerAppInterface

    class SlurmControllerAppInterface(AppBucketInterface):
        """Used by slurm-server leader to set the global slurm.conf file."""

        slurm_conf_hash = String()
        slurm_conf = FileDataInterface()
