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

## Relations

`slurm-client-ready` - a requires relation used to connect to a principal charm that provides the relation.

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
`CONTRIBUTING.md` for developer guidance.
