#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Interface for the auth-munge relation."""

from hpctlib.ext.interfaces.file import FileDataInterface
from hpctlib.interface.relation import AppBucketInterface, RelationSuperInterface
from hpctlib.interface.value import String


class AuthMungeInterface(RelationSuperInterface):
    """Super interface for the auth-munge relation."""

    def __init__(self, charm, relname: str, role=None) -> None:
        super().__init__(charm, relname, role)

        self.interface_classes[("provider", "app")] = self.AuthMungeAppInterface

    class AuthMungeAppInterface(AppBucketInterface):
        """Used by slurm-server leader to set the global munge key."""

        munge_key_hash = String()
        munge_key = FileDataInterface()
