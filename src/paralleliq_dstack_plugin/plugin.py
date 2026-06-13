from dstack.plugins import ApplyPolicy, FleetSpec, Plugin, RunSpec, get_plugin_logger

logger = get_plugin_logger(__name__)

_PIQC_RBAC_URL = "https://raw.githubusercontent.com/paralleliq/piqc/main/deploy/rbac.yaml"
_PIQC_JOB_URL = "https://raw.githubusercontent.com/paralleliq/piqc/main/deploy/scan-job.yaml"

_PIQC_MESSAGE = (
    "\n"
    "  Paralleliq — GPU fleet detected.\n"
    "  Run a free GPU waste scan on this cluster:\n"
    "\n"
    f"    kubectl apply -f {_PIQC_RBAC_URL}\n"
    f"    kubectl apply -f {_PIQC_JOB_URL}\n"
    "    kubectl logs -n kube-system job/piqc-scan\n"
    "\n"
    "  github.com/paralleliq/piqc  ·  paralleliq.ai\n"
)


def _has_gpu_resources(resources) -> bool:
    """Return True if the resources spec requests at least one GPU."""
    if resources is None:
        return False
    gpu = getattr(resources, "gpu", None)
    if gpu is None:
        return False
    count = getattr(gpu, "count", None)
    if count is None:
        return False
    min_count = getattr(count, "min", None)
    if min_count is not None and min_count >= 1:
        return True
    max_count = getattr(count, "max", None)
    if max_count is not None and max_count >= 1:
        return True
    return False


class ParalleliqApplyPolicy(ApplyPolicy):
    def on_fleet_apply(self, user: str, project: str, spec: FleetSpec) -> FleetSpec:
        resources = getattr(spec.configuration, "resources", None)
        if _has_gpu_resources(resources):
            logger.info(_PIQC_MESSAGE)
        return spec

    def on_run_apply(self, user: str, project: str, spec: RunSpec) -> RunSpec:
        resources = getattr(spec.configuration, "resources", None)
        if _has_gpu_resources(resources):
            logger.info(_PIQC_MESSAGE)
        return spec


class ParalleliqPlugin(Plugin):
    def get_apply_policies(self) -> list[ApplyPolicy]:
        return [ParalleliqApplyPolicy()]
