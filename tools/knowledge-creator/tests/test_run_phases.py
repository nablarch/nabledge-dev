"""E2E tests for run.py main() — real Phase classes with mocked claude."""
import json
import os
import sys
import shutil
import glob
import pytest
from unittest.mock import patch, MagicMock

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOL_DIR)

from run import Context
from conftest import make_mock_run_claude


def _setup_repo(tmp_path, run_id="test"):
    """テスト用リポジトリを構築し、classified.json を正しいパスに配置する。

    classified.json は ctx.classified_list_path に配置する。
    Phase A を含むテストでは Step2Classify がこのファイルを上書きする点に注意。
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    ctx = Context(version="6", repo=str(repo), concurrency=1, run_id=run_id)

    # ソースファイル
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    src_dir = repo / "tests" / "fixtures"
    src_dir.mkdir(parents=True)
    shutil.copy(os.path.join(fixtures_dir, "sample_source.rst"),
                src_dir / "sample_source.rst")

    # classified.json を ctx.classified_list_path に配置
    os.makedirs(os.path.dirname(ctx.classified_list_path), exist_ok=True)
    classified = {
        "version": "6",
        "generated_at": "2026-01-01T00:00:00Z",
        "files": [
            {
                "id": "handlers-sample-handler",
                "source_path": "tests/fixtures/sample_source.rst",
                "format": "rst",
                "filename": "sample_source.rst",
                "type": "component",
                "category": "handlers",
                "output_path": "component/handlers/handlers-sample-handler.json",
                "assets_dir": "component/handlers/assets/handlers-sample-handler/"
            }
        ]
    }
    with open(ctx.classified_list_path, "w", encoding="utf-8") as f:
        json.dump(classified, f, ensure_ascii=False, indent=2)

    # プロンプトディレクトリ（実ファイルをコピー）
    prompts_dir = repo / "tools" / "knowledge-creator" / "prompts"
    prompts_dir.mkdir(parents=True)
    real_prompts = os.path.join(TOOL_DIR, "prompts")
    for fname in os.listdir(real_prompts):
        shutil.copy(os.path.join(real_prompts, fname), prompts_dir / fname)

    # knowledge-creator.json（Phase M の update_knowledge_meta 用）
    plugin_dir = repo / ".claude" / "skills" / "nabledge-6" / "plugin"
    plugin_dir.mkdir(parents=True)
    meta = {
        "generated_at": "",
        "sources": [
            {"repo": "https://github.com/nablarch/nablarch-document", "branch": "main", "commit": ""},
            {"repo": "https://github.com/nablarch/nablarch-system-development-guide", "branch": "main", "commit": ""}
        ]
    }
    with open(plugin_dir / "knowledge-creator.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return str(repo), ctx


def _make_args(repo, phase=None, run_id="test"):
    args = MagicMock()
    args.version = "6"
    args.repo = repo
    args.phase = phase
    args.max_rounds = 1
    args.concurrency = 1
    args.dry_run = False
    args.test = None
    args.run_id = run_id
    args.yes = True
    args.regen = False
    args.target = None
    args.clean_phase = None
    return args


def _run_main(repo, args):
    """main() を実行する。

    注意点:
    1. main() は repo_root を __file__ から自動検出する。テスト用 repo を使うために
       os.path.abspath をpatchし、run.py のリポジトリルート算出時のみテスト用 repo を返す。

    2. 各Phaseモジュールの _default_run_claude を個別にpatchする。
       steps.common.run_claude の一括patchでは効かない。理由:
       各Phaseモジュールは from .common import run_claude as _default_run_claude で
       import時にローカル変数にバインド済み。
    """
    mock_claude = make_mock_run_claude()
    argv = ["run.py", "--version", "6"]
    if args.phase:
        argv += ["--phase", args.phase]

    # main() 内の repo_root = os.path.abspath(...) をテスト用 repo に差し替える
    original_abspath = os.path.abspath

    def patched_abspath(path):
        result = original_abspath(path)
        if result == original_abspath(os.path.join(TOOL_DIR, '..', '..')):
            return repo
        return result

    with patch("sys.argv", argv), \
         patch("argparse.ArgumentParser.parse_args", return_value=args), \
         patch("os.path.abspath", side_effect=patched_abspath), \
         patch("steps.phase_b_generate._default_run_claude", mock_claude), \
         patch("steps.phase_d_content_check._default_run_claude", mock_claude), \
         patch("steps.phase_e_fix._default_run_claude", mock_claude), \
         patch("steps.phase_f_finalize._default_run_claude", mock_claude):
        import run as run_module
        run_module.main()


class TestPhaseControl:
    """run.py main() のPhase制御をE2Eで検証する。"""

    def test_phase_bcdem(self, tmp_path):
        """--phase BCDEM: B→C→D→(E)→M が通しで実行される。

        Phase A を含まないため classified.json は _setup_repo のまま維持される。
        Phase間グルーコード（Phase B後の後処理含む）がエラーなく実行されることを検証。
        """
        repo, ctx = _setup_repo(tmp_path)
        args = _make_args(repo, phase="BCDEM")
        _run_main(repo, args)

        # Phase B: 知識ファイルが生成された
        knowledge_path = os.path.join(
            ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json")
        assert os.path.exists(knowledge_path), "Phase B should generate knowledge file"

        # Phase C: structure check結果が生成された
        assert os.path.exists(ctx.structure_check_path), \
            "Phase C should generate structure check results"

        # Phase M: docs が生成された（G→Fを内部で実行）
        assert os.path.isdir(ctx.docs_dir), "Phase M should generate docs directory"

        # レポートが生成された（BCDEM全フローが正常完了した証拠）
        assert os.path.exists(ctx.report_path), "Report should be generated"

    def test_phase_m_only(self, tmp_path):
        """--phase M: Mのみ実行。B/C/Dは実行されない。"""
        repo, ctx = _setup_repo(tmp_path)
        args = _make_args(repo, phase="M")
        _run_main(repo, args)

        # Phase B の成果物は生成されない
        knowledge_path = os.path.join(
            ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json")
        assert not os.path.exists(knowledge_path), "Phase B should not run"

        # Phase C の成果物は生成されない
        assert not os.path.exists(ctx.structure_check_path), "Phase C should not run"

    def test_default_phases_include_m(self, tmp_path):
        """デフォルト(ABCDEM): Phase Aを含むフルフローがエラーなく完了する。

        Phase A が classified.json を空の files リストで上書きするため
        Phase B の処理対象は0件になる。知識ファイルは生成されないが、
        全Phaseが正常に完了しレポートが生成されることを検証。
        """
        repo, ctx = _setup_repo(tmp_path)
        args = _make_args(repo, phase=None)  # デフォルト = ABCDEM
        _run_main(repo, args)

        # レポートが生成された（全Phaseが正常完了した証拠）
        assert os.path.exists(ctx.report_path), "Report should be generated"

    def test_backward_compat_gf(self, tmp_path):
        """--phase GF: G→F が実行され、Mは実行されない。"""
        repo, ctx = _setup_repo(tmp_path)
        args = _make_args(repo, phase="GF")
        _run_main(repo, args)

        # レポートが生成された
        assert os.path.exists(ctx.report_path), "Report should be generated"

    def test_phase_b_glue_code_executes(self, tmp_path):
        """Phase B完了後のグルーコードがエラーなく実行される。

        classified.json が存在する状態で Phase B のみ実行。
        source_tracker 行が残っていれば ModuleNotFoundError で失敗する。
        """
        repo, ctx = _setup_repo(tmp_path)
        args = _make_args(repo, phase="B")
        _run_main(repo, args)

        # Phase B の成果物確認
        knowledge_path = os.path.join(
            ctx.knowledge_dir, "component/handlers/handlers-sample-handler.json")
        assert os.path.exists(knowledge_path), "Phase B should generate knowledge file"
