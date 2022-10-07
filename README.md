# hpct-slurm-client-operator

## Description

A subordinate charm that installs and manages `slurmd` and `munge` daemons on a principal charm.

## Usage

> See internal xwiki article [here](https://hpc4can.ddns.net/xwiki/bin/view/Users/nuccitheboss/Nucci's%20Howtos/Setup%20HPC%20cluster%20with%20hpct%20charms/).

To deploy:

```
juju deploy ./hpct-slurm-client-operator_ubuntu-22.04-amd64.charm
```

Assuming a `hpct-xxx-principal-operator` has been deployed:

```
juju relate hpct-slurm-client-operator hpct-xxx-principal-operator
```

Assuming a `hpct-slurm-server-operator` has been deployed:

```
juju relate slurm-client:auth-munge slurm-server:auth-munge
juju relate slurm-client:slurm-controller slurm-server:slurm-controller
juju relate slurm-client:slurm-compute slurm-server:slurm-compute
```

## Relations

`auth-munge` - a requires relation used to consume the munge key of the primary slurm server.

`slurm-client-ready` - a requires relation used to connect to a principal charm that provides the relation.

`slurm-compute` - a provides relation used to serve unit information to the primary slurm server.

`slurm-controller` - a requires relation used to consume the slurm configuration served by the primary slurm server.

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
`CONTRIBUTING.md` for developer guidance.
