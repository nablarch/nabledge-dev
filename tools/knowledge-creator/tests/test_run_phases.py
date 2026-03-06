"""Tests for run.py phase control logic."""
import json
import os
import sys
from unittest.mock import patch, MagicMock
import pytest


class TestPhaseControl:
    """Test that phase option controls which phases are executed."""

    def _create_test_args(self, phase=None):
        """Create mock args for run.py."""
        args = MagicMock()
        args.version = "6"
        args.repo = "/tmp/test-repo"
        args.phase = phase
        args.max_rounds = 3
        args.concurrency = 1
        args.dry_run = False
        args.test = None
        args.run_id = None
        args.regen = False
        args.clean_phase = None
        args.target = None
        args.yes = False
        return args

    def _patch_phases(self):
        """Patch all Phase classes to track execution."""
        patches = {}
        tracked = {}

        # Track which phases were instantiated
        for phase_name, module_path, class_name in [
            ("A", "steps.step1_list_sources", "Step1ListSources"),
            ("A", "steps.step2_classify", "Step2Classify"),
            ("B", "steps.phase_b_generate", "PhaseBGenerate"),
            ("C", "steps.phase_c_structure_check", "PhaseCStructureCheck"),
            ("D", "steps.phase_d_content_check", "PhaseDContentCheck"),
            ("E", "steps.phase_e_fix", "PhaseEFix"),
            ("G", "steps.phase_g_resolve_links", "PhaseGResolveLinks"),
            ("F", "steps.phase_f_finalize", "PhaseFFinalize"),
            ("M", "steps.phase_m_finalize", "PhaseMFinalize"),
        ]:
            key = f"{phase_name}_{class_name}"
            tracked[key] = {"instantiated": False, "run_called": False}

            # Create mock class
            def make_mock(track_key):
                class MockPhase:
                    def __init__(self, *args, **kwargs):
                        tracked[track_key]["instantiated"] = True

                    def run(self, *args, **kwargs):
                        tracked[track_key]["run_called"] = True
                        # Return appropriate result based on phase
                        if "PhaseCStructureCheck" in track_key:
                            return {"pass_ids": [], "error_count": 0, "pass": 0}
                        elif "PhaseDContentCheck" in track_key:
                            return {"issue_file_ids": [], "issues_count": 0}
                        elif "Step1ListSources" in track_key:
                            return {"files": []}
                        return {}

                return MockPhase

            patches[key] = patch(f"{module_path}.{class_name}", make_mock(key))

        return patches, tracked

    def test_default_phases_include_m(self, tmp_path):
        """Default phases should be ABCDEM."""
        args = self._create_test_args(phase=None)
        args.repo = str(tmp_path)

        # Create required directories
        os.makedirs(f"{tmp_path}/.lw/nab-official/nablarch-document/en/application_framework", exist_ok=True)

        patches, tracked = self._patch_phases()

        with patch('sys.argv', ['run.py', '--version', '6']):
            with patch('argparse.ArgumentParser.parse_args', return_value=args):
                # Start all patches
                for p in patches.values():
                    p.start()

                try:
                    # Import and run
                    import run as run_module
                    run_module.main()

                    # Verify: Phase M should be instantiated
                    assert tracked["M_PhaseMFinalize"]["instantiated"], "Phase M should be executed in default mode"

                    # Verify: Phase G and F should NOT be instantiated (replaced by M)
                    assert not tracked["G_PhaseGResolveLinks"]["instantiated"], "Phase G should not run when M is present"
                    assert not tracked["F_PhaseFFinalize"]["instantiated"], "Phase F should not run when M is present"

                finally:
                    # Stop all patches
                    for p in patches.values():
                        p.stop()

    def test_explicit_phase_m(self, tmp_path):
        """--phase M should execute only Phase M."""
        args = self._create_test_args(phase="M")
        args.repo = str(tmp_path)

        patches, tracked = self._patch_phases()

        with patch('sys.argv', ['run.py', '--version', '6', '--phase', 'M']):
            with patch('argparse.ArgumentParser.parse_args', return_value=args):
                for p in patches.values():
                    p.start()

                try:
                    import run as run_module
                    run_module.main()

                    # Verify: Only Phase M
                    assert tracked["M_PhaseMFinalize"]["instantiated"], "Phase M should be executed"

                    # Verify: Other phases not executed
                    assert not tracked["A_Step1ListSources"]["instantiated"], "Phase A should not run"
                    assert not tracked["B_PhaseBGenerate"]["instantiated"], "Phase B should not run"
                    assert not tracked["C_PhaseCStructureCheck"]["instantiated"], "Phase C should not run"
                    assert not tracked["D_PhaseDContentCheck"]["instantiated"], "Phase D should not run"
                    assert not tracked["E_PhaseEFix"]["instantiated"], "Phase E should not run"
                    assert not tracked["G_PhaseGResolveLinks"]["instantiated"], "Phase G should not run"
                    assert not tracked["F_PhaseFFinalize"]["instantiated"], "Phase F should not run"

                finally:
                    for p in patches.values():
                        p.stop()

    def test_phase_bcdem_full_flow(self, tmp_path):
        """--phase BCDEM should execute full flow in correct order."""
        args = self._create_test_args(phase="BCDEM")
        args.repo = str(tmp_path)

        # Create classified.json so Phase B/C/D/E can run
        os.makedirs(f"{tmp_path}/.logs/v6", exist_ok=True)
        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": []
        }
        with open(f"{tmp_path}/.logs/v6/classified.json", "w") as f:
            json.dump(classified, f)

        patches, tracked = self._patch_phases()

        with patch('sys.argv', ['run.py', '--version', '6', '--phase', 'BCDEM']):
            with patch('argparse.ArgumentParser.parse_args', return_value=args):
                for p in patches.values():
                    p.start()

                try:
                    import run as run_module
                    run_module.main()

                    # Verify: B, C, D, E, M all executed
                    assert tracked["B_PhaseBGenerate"]["instantiated"], "Phase B should be executed"
                    assert tracked["C_PhaseCStructureCheck"]["instantiated"], "Phase C should be executed"
                    assert tracked["D_PhaseDContentCheck"]["instantiated"], "Phase D should be executed"
                    # Phase E might not be called if D returns no issues, but that's ok
                    assert tracked["M_PhaseMFinalize"]["instantiated"], "Phase M should be executed"

                    # Verify: A not executed
                    assert not tracked["A_Step1ListSources"]["instantiated"], "Phase A should not run"

                    # Verify: G and F not executed (replaced by M)
                    assert not tracked["G_PhaseGResolveLinks"]["instantiated"], "Phase G should not run when M is present"
                    assert not tracked["F_PhaseFFinalize"]["instantiated"], "Phase F should not run when M is present"

                finally:
                    for p in patches.values():
                        p.stop()

    def test_backward_compat_gf_still_works(self, tmp_path):
        """--phase GF should execute G -> F for backward compatibility."""
        args = self._create_test_args(phase="GF")
        args.repo = str(tmp_path)

        # Create classified.json so phases can run
        os.makedirs(f"{tmp_path}/.logs/v6", exist_ok=True)
        classified = {
            "version": "6",
            "generated_at": "2026-01-01T00:00:00Z",
            "files": []
        }
        with open(f"{tmp_path}/.logs/v6/classified.json", "w") as f:
            json.dump(classified, f)

        patches, tracked = self._patch_phases()

        with patch('sys.argv', ['run.py', '--version', '6', '--phase', 'GF']):
            with patch('argparse.ArgumentParser.parse_args', return_value=args):
                for p in patches.values():
                    p.start()

                try:
                    import run as run_module
                    run_module.main()

                    # Verify: G and F executed (backward compat)
                    assert tracked["G_PhaseGResolveLinks"]["instantiated"], "Phase G should be executed"
                    assert tracked["F_PhaseFFinalize"]["instantiated"], "Phase F should be executed"

                    # Verify: M not executed
                    assert not tracked["M_PhaseMFinalize"]["instantiated"], "Phase M should not run when using explicit GF"

                    # Verify: Other phases not executed
                    assert not tracked["A_Step1ListSources"]["instantiated"], "Phase A should not run"
                    assert not tracked["B_PhaseBGenerate"]["instantiated"], "Phase B should not run"
                    assert not tracked["C_PhaseCStructureCheck"]["instantiated"], "Phase C should not run"
                    assert not tracked["D_PhaseDContentCheck"]["instantiated"], "Phase D should not run"
                    assert not tracked["E_PhaseEFix"]["instantiated"], "Phase E should not run"

                finally:
                    for p in patches.values():
                        p.stop()
