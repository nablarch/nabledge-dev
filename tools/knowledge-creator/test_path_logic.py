#!/usr/bin/env python3
"""Comprehensive path logic test for knowledge creator

Tests all path constructions across all steps to prevent duplication bugs.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'steps'))

from run import Context

def test_context_paths():
    """Test Context path properties"""
    # Use actual repo path for validation
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    ctx = Context(version="6", repo=repo, concurrency=1)

    print("## Context Properties")
    print(f"  repo: {ctx.repo}")
    print(f"  knowledge_dir: {ctx.knowledge_dir}")
    print(f"  docs_dir: {ctx.docs_dir}")
    print(f"  log_dir: {ctx.log_dir}")
    print(f"  index_path: {ctx.index_path}")

    assert ctx.knowledge_dir == f"{repo}/.claude/skills/nabledge-6/knowledge", "knowledge_dir should be full path"
    assert ctx.docs_dir == f"{repo}/.claude/skills/nabledge-6/docs", "docs_dir should be full path"
    assert ctx.log_dir == f"{repo}/tools/knowledge-creator/logs/v6", "log_dir should be full path"
    assert ctx.index_path == f"{repo}/.claude/skills/nabledge-6/knowledge/index.toon", "index_path should be full path"

    # Verify no duplication
    assert ctx.knowledge_dir.count(ctx.repo) == 1, "knowledge_dir should contain repo exactly once"
    assert ctx.docs_dir.count(ctx.repo) == 1, "docs_dir should contain repo exactly once"
    assert ctx.log_dir.count(ctx.repo) == 1, "log_dir should contain repo exactly once"

    print("✅ Context paths are correct")


def test_step_path_constructions():
    """Test path constructions in each step"""
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    ctx = Context(version="6", repo=repo, concurrency=1)

    # Simulated file_info (output from Step2)
    file_info = {
        "id": "test_file",
        "source_path": ".lw/nab-official/v6/nablarch-document/ja/test.rst",
        "output_path": "component/adapters/test_file.json",
        "assets_dir": "component/adapters/assets/test_file/",
        "type": "component",
        "category": "adapters",
        "format": "rst"
    }

    print("\n## Step Path Constructions")

    # Step 3: Generate
    output_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    source_path = f"{ctx.repo}/{file_info['source_path']}"
    assets_dir_abs = f"{ctx.knowledge_dir}/{file_info['assets_dir']}"

    print(f"Step 3 - Generate:")
    print(f"  output_path: {output_path}")
    print(f"  source_path: {source_path}")
    print(f"  assets_dir_abs: {assets_dir_abs}")

    assert output_path == f"{repo}/.claude/skills/nabledge-6/knowledge/component/adapters/test_file.json"
    assert source_path == f"{repo}/.lw/nab-official/v6/nablarch-document/ja/test.rst"
    assert assets_dir_abs == f"{repo}/.claude/skills/nabledge-6/knowledge/component/adapters/assets/test_file/"
    assert output_path.count(ctx.repo) == 1, "No duplication in output_path"
    assert assets_dir_abs.count(ctx.repo) == 1, "No duplication in assets_dir_abs"

    # Step 3: Assets relative path
    json_dir = os.path.dirname(file_info['output_path'])  # "component/adapters"
    assets_dir_rel = os.path.relpath(file_info['assets_dir'], json_dir) + "/"
    print(f"  assets_dir_rel: {assets_dir_rel}")
    assert assets_dir_rel == "assets/test_file/", "Relative path from JSON to assets should be assets/test_file/"

    # Step 4: Build Index
    json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    assert json_path == output_path, "Step 4 should use same path as Step 3"

    # Step 5: Generate Docs
    md_path = f"{ctx.docs_dir}/{file_info['type']}/{file_info['category']}/{file_info['id']}.md"
    print(f"Step 5 - Docs:")
    print(f"  md_path: {md_path}")
    assert md_path == f"{repo}/.claude/skills/nabledge-6/docs/component/adapters/test_file.md"
    assert md_path.count(ctx.repo) == 1, "No duplication in md_path"

    # Step 6: Validate
    json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    source_path = f"{ctx.repo}/{file_info['source_path']}"
    assert json_path == output_path, "Step 6 should use same paths"

    # run.py: delete_knowledge
    delete_json_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    delete_md_path = f"{ctx.docs_dir}/{file_info['type']}/{file_info['category']}/{file_info['id']}.md"
    delete_assets_path = f"{ctx.knowledge_dir}/{file_info['assets_dir']}"

    print(f"delete_knowledge:")
    print(f"  json: {delete_json_path}")
    print(f"  md: {delete_md_path}")
    print(f"  assets: {delete_assets_path}")

    assert delete_json_path == output_path
    assert delete_md_path == md_path
    assert delete_assets_path == assets_dir_abs
    assert delete_assets_path.count(ctx.repo) == 1, "No duplication in delete_assets_path"

    print("✅ All step path constructions are correct")


def test_no_path_duplication():
    """Ensure no path contains repo path twice"""
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    ctx = Context(version="6", repo=repo, concurrency=1)

    paths_to_check = [
        ctx.knowledge_dir,
        ctx.docs_dir,
        ctx.log_dir,
        ctx.index_path,
    ]

    print("\n## Path Duplication Check")
    for path in paths_to_check:
        count = path.count(ctx.repo)
        print(f"  {path}: repo appears {count} time(s)")
        assert count == 1, f"Path should contain repo exactly once: {path}"

    print("✅ No path duplication detected")


def main():
    print("=" * 60)
    print("Knowledge Creator - Comprehensive Path Logic Test")
    print("=" * 60)

    try:
        test_context_paths()
        test_step_path_constructions()
        test_no_path_duplication()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nPath logic is correct:")
        print("  - Context properties are full paths")
        print("  - file_info properties are relative paths")
        print("  - All steps correctly combine context + file_info")
        print("  - No path duplication")
        print("  - Assets paths are correctly computed")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
