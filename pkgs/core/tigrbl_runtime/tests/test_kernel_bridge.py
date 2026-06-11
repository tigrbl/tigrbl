from tigrbl_kernel import Kernel as KernelFromKernel

from tigrbl_runtime.runtime import Kernel as KernelFromRuntime
from tigrbl_runtime.runtime.kernel import bind_runtime_executor
from tigrbl_runtime.executors.kernel_executor import _run, _run_phase_chain


def test_runtime_uses_kernel_class_from_tigrbl_kernel() -> None:
    assert KernelFromRuntime is KernelFromKernel


def test_runtime_does_not_attach_executor_methods_to_kernel_on_import() -> None:
    assert getattr(KernelFromRuntime, "_run", None) is not _run
    assert getattr(KernelFromRuntime, "_run_phase_chain", None) is not _run_phase_chain


def test_runtime_bridge_attaches_executor_methods_explicitly() -> None:
    original_run = getattr(KernelFromRuntime, "_run", None)
    original_run_phase_chain = getattr(KernelFromRuntime, "_run_phase_chain", None)
    try:
        bind_runtime_executor(KernelFromRuntime)

        assert KernelFromRuntime._run is _run
        assert KernelFromRuntime._run_phase_chain is _run_phase_chain
    finally:
        if original_run is None:
            try:
                delattr(KernelFromRuntime, "_run")
            except AttributeError:
                pass
        else:
            KernelFromRuntime._run = original_run
        if original_run_phase_chain is None:
            try:
                delattr(KernelFromRuntime, "_run_phase_chain")
            except AttributeError:
                pass
        else:
            KernelFromRuntime._run_phase_chain = original_run_phase_chain


def test_runtime_bridge_returns_kernel_class() -> None:
    original_run = getattr(KernelFromRuntime, "_run", None)
    original_run_phase_chain = getattr(KernelFromRuntime, "_run_phase_chain", None)
    try:
        assert bind_runtime_executor(KernelFromRuntime) is KernelFromRuntime
    finally:
        if original_run is None:
            try:
                delattr(KernelFromRuntime, "_run")
            except AttributeError:
                pass
        else:
            KernelFromRuntime._run = original_run
        if original_run_phase_chain is None:
            try:
                delattr(KernelFromRuntime, "_run_phase_chain")
            except AttributeError:
                pass
        else:
            KernelFromRuntime._run_phase_chain = original_run_phase_chain


def test_runtime_bridge_preserves_executor_identity_when_explicit() -> None:
    original_run = getattr(KernelFromRuntime, "_run", None)
    original_run_phase_chain = getattr(KernelFromRuntime, "_run_phase_chain", None)
    try:
        bind_runtime_executor(KernelFromRuntime)

        assert KernelFromRuntime._run is _run
        assert KernelFromRuntime._run_phase_chain is _run_phase_chain
    finally:
        if original_run is None:
            try:
                delattr(KernelFromRuntime, "_run")
            except AttributeError:
                pass
        else:
            KernelFromRuntime._run = original_run
        if original_run_phase_chain is None:
            try:
                delattr(KernelFromRuntime, "_run_phase_chain")
            except AttributeError:
                pass
        else:
            KernelFromRuntime._run_phase_chain = original_run_phase_chain
