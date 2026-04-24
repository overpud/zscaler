# Kubernetes Request-Based Autoscaler

A Python Kubernetes operator that scales a deployment from external request-count
signals. The project demonstrates Linux systems engineering skills around
Kubernetes controllers, custom resources, RBAC, container hardening, service
discovery, and repeatable cluster operations.

## What It Does

The operator watches a namespaced `ZScaler` custom resource and periodically:

1. Fetches a request count from an internal HTTP service.
2. Reads the current replica count for a target deployment.
3. Calculates requests per replica.
4. Patches the deployment scale subresource when thresholds are crossed.
5. Writes the latest decision into the custom resource status.

```text
ZScaler CR
    |
    v
Kopf operator  --->  process-counter service
    |
    v
apps/v1 deployments/scale
    |
    v
nginx-deployment replicas
```

## Engineering Highlights

- Kubernetes operator built with Python and Kopf.
- CustomResourceDefinition with OpenAPI validation, defaults, printer columns,
  and status subresource support.
- Namespaced least-privilege RBAC for deployment reads, scale patches, custom
  resource watches, status updates, and event writes.
- Non-root container images based on `python:3.11-slim`.
- Kubernetes manifests with resource requests, limits, readiness probes,
  liveness probes, dropped Linux capabilities, and seccomp defaults.
- Testable autoscaling policy separated from Kubernetes API calls.
- Unit tests for scale-up, scale-down, max-replica, zero-replica recovery, and
  invalid policy handling.
- Makefile workflow for build, deploy, logs, status, and cleanup.
- GitHub Actions workflow for Python tests and syntax checks.

## Repository Layout

```text
case-study/
  autoscaler/
    operator.py                  # Kopf handler and Kubernetes reconciliation
    scaling.py                   # Pure autoscaling policy logic
    utils.py                     # Kubernetes client helpers
    kubernetes/                  # CRD, RBAC, operator deployment, sample CR
  process-counter/
    api.py                       # HTTP service exposing synthetic request count
    deployment/                  # Service and deployment manifests
  dummy-application/
    deployment.yaml              # Target deployment scaled by the operator
  tests/
    test_scaling.py              # Unit tests for autoscaling behavior
  Makefile
```

## Quick Start

Requirements:

- Python 3.11+
- Docker
- kubectl
- A local Kubernetes cluster such as kind or minikube

Run the tests:

```bash
cd case-study
make test
```

Build the local images:

```bash
make build
```

For kind, load the images into the cluster:

```bash
kind load docker-image zscaler-operator:latest
kind load docker-image process-counter:latest
```

Deploy everything into a demo namespace:

```bash
make deploy
```

Watch the custom resource and target deployment:

```bash
make status
kubectl get zscalers -n zscaler-demo -w
kubectl get deploy nginx-deployment -n zscaler-demo -w
```

Follow operator logs:

```bash
make logs
```

Clean up:

```bash
make undeploy
```

## Custom Resource Example

```yaml
apiVersion: zapata.test.com/v1
kind: ZScaler
metadata:
  name: nginx-request-autoscaler
spec:
  deploymentName: nginx-deployment
  serviceName: pcd-service
  minReplicas: 1
  maxReplicas: 4
  scaleUpThreshold: 50
  scaleDownThreshold: 20
```

## Scaling Policy

The request counter returns a synthetic request-count value. The operator divides
that value by the current replica count:

- Scale up by one replica when requests per replica are greater than or equal to
  `scaleUpThreshold`.
- Scale down by one replica when requests per replica are less than or equal to
  `scaleDownThreshold`.
- Never scale below `minReplicas`.
- Never scale above `maxReplicas`.
- Recover a zero-replica deployment by returning it to `minReplicas`.

## Useful Commands

```bash
kubectl describe zscaler nginx-request-autoscaler -n zscaler-demo
kubectl get zscalers -n zscaler-demo -o yaml
kubectl logs -n zscaler-demo deploy/zscaler-operator
kubectl scale deploy nginx-deployment -n zscaler-demo --replicas=0
```

## Resume Bullet

Built a Kubernetes custom autoscaler operator in Python using Kopf,
CustomResourceDefinitions, least-privilege RBAC, hardened containers, and
unit-tested scaling logic to scale workloads from external request metrics.
