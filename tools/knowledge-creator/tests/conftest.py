import os
import sys
import json
import shutil
import pytest
import subprocess

TOOL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOL_DIR)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    path = os.path.join(FIXTURES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f) if name.endswith(".json") else f.read()


def make_mock_run_claude(generate_output=None, findings_output=None,
                         fix_output=None, classify_output=None):
    """Generate a mock run_claude function.

    Determines which Phase is calling by inspecting json_schema content.
    Returns the corresponding mock output.
    """
    default_knowledge = load_fixture("sample_knowledge.json")

    _generate = generate_output or {
        "knowledge": default_knowledge,
        "trace": {
            "sections": [
                {"section_id": "overview", "source_heading": "概要",
                 "heading_level": "h2", "h3_split": False,
                 "h3_split_reason": "800 chars < 2000"},
                {"section_id": "module-list", "source_heading": "モジュール一覧",
                 "heading_level": "h2", "h3_split": False,
                 "h3_split_reason": "600 chars < 2000"}
            ]
        }
    }
    _findings = findings_output or {
        "file_id": "handlers-sample-handler",
        "status": "clean",
        "findings": []
    }
    _fix = fix_output or default_knowledge
    _classify = classify_output or {
        "patterns": [],
        "reasoning": [
            {"pattern": "nablarch-batch", "matched": False,
             "evidence": "No batch content"}
        ]
    }

    def mock_fn(prompt, timeout=600, json_schema=None):
        schema_str = json.dumps(json_schema) if json_schema else ""
        if "trace" in schema_str:
            output = _generate
        elif "findings" in schema_str:
            output = _findings
        elif "reasoning" in schema_str:
            output = _classify
        else:
            output = _fix

        return subprocess.CompletedProcess(
            args=["claude", "-p"], returncode=0,
            stdout=json.dumps(output, ensure_ascii=False), stderr=""
        )

    return mock_fn


@pytest.fixture
def test_repo(tmp_path):
    """Build a temporary repo with classified.json and source file."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Source file
    src_dir = repo / "tests" / "fixtures"
    src_dir.mkdir(parents=True)
    shutil.copy(os.path.join(FIXTURES_DIR, "sample_source.rst"), src_dir / "sample_source.rst")

    # classified.json (required by Phase G for doc index building)
    log_dir = repo / "tools" / "knowledge-creator" / "logs" / "v6"
    log_dir.mkdir(parents=True)
    classified = load_fixture("sample_classified.json")
    with open(log_dir / "classified.json", "w", encoding="utf-8") as f:
        json.dump(classified, f, ensure_ascii=False, indent=2)

    # trace directory (required by Phase G for label index building)
    trace_dir = log_dir / "trace"
    trace_dir.mkdir(parents=True, exist_ok=True)

    # knowledge directory
    (repo / ".claude" / "skills" / "nabledge-6" / "knowledge" / "component" / "handlers").mkdir(parents=True)

    # prompts directory - copy real prompts
    prompts_dir = repo / "tools" / "knowledge-creator" / "prompts"
    prompts_dir.mkdir(parents=True)
    real_prompts = os.path.join(TOOL_DIR, "prompts")
    if os.path.exists(real_prompts):
        for f in os.listdir(real_prompts):
            shutil.copy(os.path.join(real_prompts, f), prompts_dir / f)

    return str(repo)


@pytest.fixture
def ctx(test_repo):
    # Import Context from run.py
    sys.path.insert(0, TOOL_DIR)
    from run import Context
    return Context(version="6", repo=test_repo, concurrency=1)


@pytest.fixture
def mock_claude():
    return make_mock_run_claude()
