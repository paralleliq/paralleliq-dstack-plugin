# paralleliq-dstack-plugin

A [dstack](https://dstack.ai) plugin that surfaces [piqc](https://github.com/paralleliq/piqc) — Paralleliq's open-source GPU waste scanner — whenever a GPU fleet or run is applied to a dstack project.

## What it does

When a user runs `dstack apply` on a fleet or task that requests GPU resources, the plugin prints a one-time message showing how to run a GPU waste scan against the cluster:

```
╔══════════════════════════════════════════════════════════════════╗
║  Paralleliq — GPU fleet detected                                 ║
║                                                                  ║
║  Run a free GPU waste scan on this cluster:                      ║
║                                                                  ║
║  kubectl apply -f https://.../deploy/rbac.yaml                   ║
║  kubectl apply -f https://.../deploy/scan-job.yaml               ║
║  kubectl logs -n kube-system job/piqc-scan                       ║
║                                                                  ║
║  github.com/paralleliq/piqc  ·  paralleliq.ai                   ║
╚══════════════════════════════════════════════════════════════════╝
```

The two `kubectl` commands:
1. Apply RBAC — creates a `ServiceAccount`, `ClusterRole`, and `ClusterRoleBinding` scoped to what piqc needs
2. Run the scan — launches a one-shot K8s Job using `ghcr.io/paralleliq/piqc:latest`

Results appear in the job logs. The job auto-deletes after 10 minutes.

## Why kubectl instead of a dstack task?

piqc needs cluster-wide Kubernetes API access — to list pods, deployments, and nodes, and to exec into pods to run `nvidia-smi`. dstack does not currently support specifying a `serviceAccountName` in task configuration, so a dstack task would run with the namespace default service account and have no cluster permissions.

Using standard K8s manifests lets piqc work correctly on any Kubernetes cluster, dstack-managed or not.

## Installation

Install on the server where dstack is running:

```bash
pip install paralleliq-dstack-plugin
```

dstack discovers plugins automatically via Python entry points — no additional configuration required.

## Requirements

- dstack >= 0.19 (server-side installation)
- kubectl access to the cluster (for running the scan commands)

## piqc

piqc is open-source. Source and docs: [github.com/paralleliq/piqc](https://github.com/paralleliq/piqc)

---

Built by [Paralleliq](https://paralleliq.ai)
