#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface for the slurm-compute relation."""

from hpctlib.interface.relation import RelationSuperInterface, UnitBucketInterface
from hpctlib.interface.value import Integer, String
from hpctlib.interface.value.network import IPAddress


class SlurmComputeInterface(RelationSuperInterface):
    """Super interface for the slurm-compute relation."""

    def __init__(self, charm, relname: str, role=None) -> None:
        super().__init__(charm, relname, role)

        self.interface_classes[("provider", "unit")] = self.SlurmComputeUnitInterface

    class SlurmComputeUnitInterface(UnitBucketInterface):
        """Used by slurm-compute nodes to provide information about themselves."""

        hostname = String()
        ip_address = IPAddress()
        cpu_count = Integer()
        free_memory = Integer()
