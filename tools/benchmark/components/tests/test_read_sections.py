"""Integration tests for read-sections.sh."""
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "read-sections.sh"
)


@pytest.fixture()
def knowledge_dir():
    """Create a minimal skill directory with knowledge files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = Path(tmpdir)
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        knowledge_dir = skill_dir / "knowledge"
        knowledge_dir.mkdir()

        scripts_dir.joinpath("read-sections.sh").write_bytes(
            SCRIPT_PATH.read_bytes()
        )
        scripts_dir.joinpath("read-sections.sh").chmod(0o755)

        sub_dir = knowledge_dir / "component" / "libraries"
        sub_dir.mkdir(parents=True)
        sub_dir.joinpath("libraries-dao.json").write_text(
            json.dumps({
                "title": "ユニバーサルDAO",
                "sections": [
                    {
                        "id": "overview",
                        "title": "機能概要",
                        "content": "UniversalDaoは汎用データアクセス機能です。",
                    },
                    {
                        "id": "usage",
                        "title": "使用方法",
                        "content": "batchUpdateメソッドで一括更新できます。",
                    },
                ],
            }),
            encoding="utf-8",
        )

        yield skill_dir


def _run(skill_dir: Path, *pairs: str) -> str:
    script = skill_dir / "scripts" / "read-sections.sh"
    result = subprocess.run(
        ["bash", str(script), *pairs],
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
    )
    return result.stdout


class TestTitleAndContent:
    """Title + content output in the expected format."""

    def test_single_section(self, knowledge_dir):
        output = _run(
            knowledge_dir,
            "component/libraries/libraries-dao.json:overview",
        )
        assert "=== component/libraries/libraries-dao.json : overview ===" in output
        assert "# ユニバーサルDAO > 機能概要" in output
        assert "UniversalDaoは汎用データアクセス機能です。" in output
        assert "=== END ===" in output

    def test_multiple_sections(self, knowledge_dir):
        output = _run(
            knowledge_dir,
            "component/libraries/libraries-dao.json:overview",
            "component/libraries/libraries-dao.json:usage",
        )
        assert output.count("=== END ===") == 2
        assert "# ユニバーサルDAO > 機能概要" in output
        assert "# ユニバーサルDAO > 使用方法" in output
        assert "batchUpdateメソッドで一括更新できます。" in output


class TestSectionNotFound:
    """SECTION_NOT_FOUND when section ID doesn't exist."""

    def test_missing_section(self, knowledge_dir):
        output = _run(
            knowledge_dir,
            "component/libraries/libraries-dao.json:nonexistent",
        )
        assert "SECTION_NOT_FOUND" in output
        assert "=== END ===" in output


class TestFileNotFound:
    """FILE_NOT_FOUND when knowledge file doesn't exist."""

    def test_missing_file(self, knowledge_dir):
        output = _run(knowledge_dir, "no-such-file.json:s1")
        assert "FILE_NOT_FOUND" in output
        assert "=== END ===" in output


class TestErrorHandling:
    """Error handling for invalid inputs."""

    def test_no_arguments(self, knowledge_dir):
        script = knowledge_dir / "scripts" / "read-sections.sh"
        result = subprocess.run(
            ["bash", str(script)],
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
        )
        assert result.returncode == 1
        assert "Usage" in result.stderr

    def test_path_traversal_rejected(self, knowledge_dir):
        script = knowledge_dir / "scripts" / "read-sections.sh"
        result = subprocess.run(
            ["bash", str(script), "../etc/passwd:s1"],
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
        )
        assert result.returncode == 1
        assert "Invalid file path" in result.stderr

    def test_absolute_path_rejected(self, knowledge_dir):
        script = knowledge_dir / "scripts" / "read-sections.sh"
        result = subprocess.run(
            ["bash", str(script), "/etc/passwd:s1"],
            capture_output=True,
            text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
        )
        assert result.returncode == 1
        assert "Invalid file path" in result.stderr
