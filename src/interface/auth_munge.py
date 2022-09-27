#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface for the auth-munge relation."""

from hpctlib.interface.relation import (
    AppBucketInterface,
    RelationSuperInterface,
    UnitBucketInterface,
)
from hpctlib.ext.interfaces.file import FileDataInterface


class AuthMungeInterface(RelationSuperInterface):
    """Super interface for the auth-munge relation."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.interface_classes[("provider", "app")] = self.AuthMungeAppInterface
        self.interface_classes[("requirer", "unit")] = self.AuthMungeUnitInterface

    class AuthMungeAppInterface(AppBucketInterface):
        """Used by slurm-server leader to set the global munge key."""

        munge_key = FileDataInterface()

    class AuthMungeUnitInterface(UnitBucketInterface):
        """Used by slurm-client units to consume the global munge key."""

        munge_key = FileDataInterface()
