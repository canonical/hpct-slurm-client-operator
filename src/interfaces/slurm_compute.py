#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface for the slurm-compute relation."""

from hpctinterfaces import interface_registry
from hpctinterfaces.relation import RelationSuperInterface, UnitBucketInterface
from hpctinterfaces.value import Integer, String
from hpctinterfaces.value.network import IPAddress


class SlurmComputeSuperInterface(RelationSuperInterface):
    """Super interface for the slurm-compute relation."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.interface_classes[("provider", "unit")] = self.SlurmComputeUnitInterface

    class SlurmComputeUnitInterface(UnitBucketInterface):
        """Used by slurm-compute nodes to provide information about themselves."""

        nonce = String("")
        hostname = String("")
        ip_address = IPAddress("0.0.0.0")
        cpu_count = Integer(0)
        free_memory = Integer(0)


interface_registry.register("relation-slurm-compute", SlurmComputeSuperInterface)
