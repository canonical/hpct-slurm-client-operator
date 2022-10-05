#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface for the slurm-controller relation."""

from hpctinterfaces.ext.file import FileDataInterface
from hpctinterfaces.relation import AppBucketInterface, RelationSuperInterface
from hpctinterfaces.value import String


class SlurmControllerSuperInterface(RelationSuperInterface):
    """Super interface for the slurm-controller relation."""

    def __init__(self, charm, relname: str, role=None) -> None:
        super().__init__(charm, relname, role)

        self.interface_classes[("provider", "app")] = self.SlurmControllerAppInterface

    class SlurmControllerAppInterface(AppBucketInterface):
        """Used by slurm-server leader to set the global slurm.conf file."""

        nonce = String("")
        slurm_conf = FileDataInterface()
