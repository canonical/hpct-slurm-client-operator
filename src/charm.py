#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""HPC Team SLURM client charm."""

import logging

from hpctlib.ops.charm.service import ServiceCharm
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class SlurmClientCharm(ServiceCharm):

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)


if __name__ == "__main__":
    main(SlurmClientCharm)
