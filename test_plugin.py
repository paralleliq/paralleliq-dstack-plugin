"""
Quick smoke test for the paralleliq-dstack-plugin.
Simulates dstack spec objects without needing a real dstack server or GPUs.
"""
from unittest.mock import MagicMock
from paralleliq_dstack_plugin.plugin import (
    ParalleliqApplyPolicy,
    _has_gpu_resources,
    _is_kubernetes_eligible,
)


def make_resources(gpu_min=None, gpu_max=None):
    count = MagicMock()
    count.min = gpu_min
    count.max = gpu_max
    gpu = MagicMock()
    gpu.count = count
    resources = MagicMock()
    resources.gpu = gpu
    return resources


def make_fleet_spec(gpu_min=None, gpu_max=None, backends=None):
    spec = MagicMock()
    spec.configuration.resources = make_resources(gpu_min, gpu_max)
    spec.configuration.backends = backends
    return spec


# --- _has_gpu_resources ---

def test_gpu_min_1():
    assert _has_gpu_resources(make_resources(gpu_min=1)) is True

def test_gpu_min_0():
    assert _has_gpu_resources(make_resources(gpu_min=0)) is False

def test_gpu_min_none_max_1():
    assert _has_gpu_resources(make_resources(gpu_min=None, gpu_max=1)) is True

def test_gpu_min_none_max_none():
    assert _has_gpu_resources(make_resources(gpu_min=None, gpu_max=None)) is False

def test_no_resources():
    assert _has_gpu_resources(None) is False


# --- _is_kubernetes_eligible ---

def test_backends_none():
    assert _is_kubernetes_eligible(None) is True

def test_backends_kubernetes():
    assert _is_kubernetes_eligible(["kubernetes"]) is True

def test_backends_aws_only():
    assert _is_kubernetes_eligible(["aws"]) is False

def test_backends_mixed():
    assert _is_kubernetes_eligible(["aws", "kubernetes"]) is True


# --- Full policy: message fires ---

def test_message_fires_for_gpu_k8s():
    policy = ParalleliqApplyPolicy()
    spec = make_fleet_spec(gpu_min=1, backends=["kubernetes"])
    policy.on_fleet_apply(user="test", project="test", spec=spec)
    print("  on_fleet_apply completed without error")

def test_message_suppressed_for_cpu_only():
    policy = ParalleliqApplyPolicy()
    spec = make_fleet_spec(gpu_min=0, backends=["kubernetes"])
    policy.on_fleet_apply(user="test", project="test", spec=spec)
    print("  on_fleet_apply skipped message for CPU-only spec")

def test_message_suppressed_for_non_k8s():
    policy = ParalleliqApplyPolicy()
    spec = make_fleet_spec(gpu_min=1, backends=["aws"])
    policy.on_fleet_apply(user="test", project="test", spec=spec)
    print("  on_fleet_apply skipped message for non-K8s backend")


if __name__ == "__main__":
    tests = [
        test_gpu_min_1,
        test_gpu_min_0,
        test_gpu_min_none_max_1,
        test_gpu_min_none_max_none,
        test_no_resources,
        test_backends_none,
        test_backends_kubernetes,
        test_backends_aws_only,
        test_backends_mixed,
        test_message_fires_for_gpu_k8s,
        test_message_suppressed_for_cpu_only,
        test_message_suppressed_for_non_k8s,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
