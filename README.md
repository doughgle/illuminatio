# illuminatio - The kubernetes network policy validator

[![Build Status](https://github.com/doughgle/illuminatio/actions/workflows/ci.yml/badge.svg)](https://github.com/doughgle/illuminatio/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/doughgle/illuminatio/branch/master/graph/badge.svg)](https://codecov.io/gh/doughgle/illuminatio)
[![Docker Image](https://img.shields.io/badge/container-GHCR-blue)](https://github.com/doughgle/illuminatio/pkgs/container/illuminatio)

![logo](/img/logo_small.png)

illuminatio is a tool for automatically testing kubernetes network policies.
Simply execute `illuminatio clean run`
and illuminatio will scan your kubernetes cluster for network policies, build test cases accordingly and execute them
to determine if the policies are in effect.

An overview of the concept is visualized in [the concept doc](docs/concept.md).

## Demo

![Demo with NetworkPolicy enabled](img/demo-netpol-enabled.gif)

Watch it on asciinema with [NetworkPolicy enabled](https://asciinema.org/a/273548) or with [NetworkPolicy disabled](https://asciinema.org/a/273556).

## Getting started

Follow these instructions to get illuminatio up and running.

## Prerequisites

- Python 3.12 or greater
- Pip 3

## Installation

### Using Container Images

The easiest way to use illuminatio is via container images from GitHub Container Registry:

```bash
docker run --rm \
--add-host=host.docker.internal:host-gateway \
-v $HOME/.kube/config:/kubeconfig \
ghcr.io/doughgle/illuminatio:master \
illuminatio clean run
```

### Using Python Package

with pip:

```bash
pip3 install illuminatio
```

or directly from the repository:

```bash
pip3 install git+https://github.com/doughgle/illuminatio
```

### Kubectl plugin

In order to use `illuminatio` as a [kubectl plugin](https://kubernetes.io/docs/tasks/extend-kubectl/kubectl-plugins) run the following command:

```bash
ln -s $(which illuminatio) /usr/local/bin/kubectl-illuminatio
```

And now cross check that the plugin exists:

```bash
kubectl plugin list --name-only | grep illuminatio
The following compatible plugins are available:

kubectl-illuminatio
```

## Example Usage

Create a Deployment to test with:

```bash
kubectl create deployment web --image=nginx
kubectl expose deployment web --port 80 --target-port 80
```

Define and create a NetworkPolicy for your Deployment:

```bash
cat <<EOF | kubectl create -f -
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: web-deny-all
spec:
  podSelector:
    matchLabels:
      app: web
  ingress: []
EOF
```

Test your newly created NetworkPolicy:

```bash
illuminatio clean run
Starting cleaning resources with policies ['on-request', 'always']
Deleting namespaces [] with cleanup policy on-request
Deleting namespaces [] with cleanup policy always
Deleting DSs in default with cleanup policy on-request
Deleting pods in default with cleanup policy on-request
Deleting svcs in default with cleanup policy on-request
Deleting CfgMaps in default with cleanup policy on-request
Deleting CRBs  with cleanup policy on-request globally
Deleting SAs in default with cleanup policy on-request
Deleting DSs in default with cleanup policy always
Deleting pods in default with cleanup policy always
Deleting svcs in default with cleanup policy always
Deleting CfgMaps in default with cleanup policy always
Deleting CRBs  with cleanup policy always globally
Deleting SAs in default with cleanup policy always
Finished cleanUp

Starting test generation and run.
Got cases: [NetworkTestCase(from=ClusterHost(namespace=default, podLabels={'app': 'web'}), to=ClusterHost(namespace=default, podLabels={'app': 'web'}), port=-*)]
Generated 1 cases in 0.0701 seconds
FROM             TO               PORT
default:app=web  default:app=web  -*

Using existing cluster role
Creating cluster role binding
TestResults: {'default:app=web': {'default:app=web': {'-*': {'success': True}}}}
Finished running 1 tests in 18.7413 seconds
FROM             TO               PORT  RESULT
default:app=web  default:app=web  -*    success
```

The `clean` keyword assures that illuminatio clears all potentially existing resources created in past illuminatio runs to prevent potential issues, however no user generated resources are affected.

*PLEASE NOTE* that currently each new run requires a clean, as the runners do not continuously look for new cases.

For the case that you really want to keep the generated resources you are free to omit the `clean` keyword.

If you are done testing you might want to easily delete all resources created by illuminatio:

```bash
illuminatio clean
```

To preview generated test cases without running tests use `illuminatio run`'s `--dry` option:

```bash
illuminatio run --dry
Starting test generation and run.
Got cases: [NetworkTestCase(from=ClusterHost(namespace=default, podLabels={'app': 'web'}), to=ClusterHost(namespace=default, podLabels={'app': 'web'}), port=-*)]
Generated 1 cases in 0.0902 seconds
FROM             TO               PORT
default:app=web  default:app=web  -*

Skipping test execution as --dry was set
```

All options and further information can be found using the `--help` flag on any level:

```bash
illuminatio --help
```

```Bash
Usage: illuminatio [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  --incluster
  --help               Show this message and exit.

Commands:
  clean
  run
```

## Running Tests

To run the unit tests for illuminatio, you can use pytest:

```bash
# Run all unit tests
pytest

# Run unit tests and generate coverage report
pytest --cov illuminatio --cov-report term-missing

# Skip end-to-end tests (which require a running Kubernetes cluster)
pytest -m "not e2e"

# Run only slow tests
pytest -m slow

# Run tests with detailed output
pytest --verbose
```

For more pytest options, see the configuration in `pyproject.toml` or run `pytest --help`.

## Docker Usage

Instead of installing the `illumnatio` cli on your machine you can also use our Docker image.
You will need to provide the `kubeconfig` to the container and probably some certificates:

```bash
docker run -ti -v ~/.kube/config:/kubeconfig:ro doughgle/illuminatio:master illuminatio clean run
```

Please note that some external authentication mechanisms (e.g. GCP / gcloud CLI) don't work correctly inside the container.

### Minikube

Minikube will store the certificates in the users home so we need to pass these to the container:

```bash
docker run -ti -v "${HOME}/.minikube":"${HOME}/.minikube" -v "${HOME}/.kube:"/home/illuminatio/.kube:ro doughgle/illuminatio illuminatio:master clean run
```

If the minikube VM is not reachable from your container try to pass the `--net=host` flag to the docker run command.

## Compatibility

illuminatio has been tested with the following Python versions:
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

illuminatio is confirmed to be working properly with the following kubernetes environments:
- minikube v0.34.1, kubernetes v1.13.3
- Google Kubernetes Engine, v1.12.8-gke.10
- kubeadm 1.15.0-00, kubernetes v1.15.2

### PodSecurityPolicy

If your cluster has the [PodSecurityPolicy](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/#podsecuritypolicy) Admission Controller you must ensure that the illuminatio runner has the following rights to be created:

- Wants to run as root
- Needs the `SYS_ADMIN` capability
- Needs `allowPrivilegeEscalation: true`
- Needs access to the `hostPath` for the network namespaces and the cri socket

A `PodSecurityPolicy` granting these privileges needs to be bound to the `illuminatio-runner` `ServiceAccount` in the `illuminatio` namespace.
For more details look at the [illuminatio DaemonSet](src/illuminatio/manifests/containerd-daemonset.yaml)

## References

The logo was created by Pia Blum.

Example Network Policies are inspired by
[kubernetes-network-policy-recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes)

Presentation from [ContainerDays 2019](https://www.youtube.com/watch?v=eEkTvAez8HA&list=PLHhKcdBlprMdg-fwPD1b3IjBRR_Ga09H0&index=36), [slides](https://www.inovex.de/de/content-pool/vortraege/network-policies)

There is also a blog post about the background of illuminatio: [illuminatio-kubernetes-network-policy-validator](https://www.inovex.de/blog/illuminatio-kubernetes-network-policy-validator/)

## Contributing

We are happy to read your [issues](https://github.com/inovex/illuminatio/issues) and accept your [Pull Requests.](https://github.com/inovex/illuminatio/compare)
This project uses the [standard github flow](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork).
For more information on developing illuminatio refer to [the development docs](docs/developing.md).

## License

This project excluding the logo is licensed under the terms of the Apache 2.0 license.
The logo is licensed under the terms of the CC BY-NC-ND 4.0 license.
