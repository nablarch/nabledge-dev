"""Tests for nc.sh command routing.

Strategy: Replace python with a stub that prints the command it received,
then verify nc.sh routes to the correct command with correct arguments.
"""
import os
import subprocess
import pytest
import tempfile
import stat

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NC_SH = os.path.join(TOOL_DIR, "nc.sh")


@pytest.fixture
def stub_env(tmp_path):
    """Create a stub python that logs commands instead of executing them."""
    stub_script = tmp_path / "python"
    stub_script.write_text(
        '#!/bin/bash\n'
        'echo "CMD: $@"\n'
    )
    stub_script.chmod(stub_script.stat().st_mode | stat.S_IEXEC)

    env = os.environ.copy()
    env["PYTHON"] = str(stub_script)
    env["PATH"] = str(tmp_path) + ":" + env.get("PATH", "")
    return env


def _run_nc(args, env):
    """Run nc.sh with stub python and return stdout."""
    result = subprocess.run(
        ["bash", NC_SH] + args,
        capture_output=True, text=True, env=env
    )
    return result


class TestGenCommand:

    def test_gen_calls_clean_then_run(self, stub_env):
        result = _run_nc(["gen", "6"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 2, f"Expected 2 commands, got: {lines}"
        assert "clean.py" in lines[0] and "--version 6" in lines[0]
        assert "run.py" in lines[1] and "--version 6" in lines[1]

    def test_gen_resume_skips_clean(self, stub_env):
        result = _run_nc(["gen", "6", "--resume"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1, f"Expected 1 command, got: {lines}"
        assert "run.py" in lines[0]
        assert "clean.py" not in lines[0]


class TestRegenCommand:

    def test_regen_without_target_uses_regen_flag(self, stub_env):
        result = _run_nc(["regen", "6"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        assert "--regen" in lines[0]

    def test_regen_with_target_uses_phase_and_clean(self, stub_env):
        result = _run_nc(["regen", "6", "--target", "test-id"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        cmd = lines[0]
        assert "--phase BCDEM" in cmd
        assert "--clean-phase BD" in cmd
        assert "--target test-id" in cmd


class TestFixCommand:

    def test_fix_uses_phase_cdem_and_clean_d(self, stub_env):
        result = _run_nc(["fix", "6"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        cmd = lines[0]
        assert "--phase CDEM" in cmd
        assert "--clean-phase D" in cmd

    def test_fix_with_target_passes_target(self, stub_env):
        result = _run_nc(["fix", "6", "--target", "test-id"], stub_env)
        lines = [l for l in result.stdout.splitlines() if l.startswith("CMD:")]
        assert len(lines) == 1
        assert "--target test-id" in lines[0]


class TestErrorHandling:

    def test_unknown_command_exits_nonzero(self, stub_env):
        result = _run_nc(["unknown", "6"], stub_env)
        assert result.returncode != 0

    def test_no_args_exits_nonzero(self, stub_env):
        result = _run_nc([], stub_env)
        assert result.returncode != 0
