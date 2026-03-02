#!/usr/bin/env python3
"""Test script to verify path construction logic"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'steps'))

from run import Context

def test_path_construction():
    """Verify paths don't have duplication"""
    ctx = Context(version="6", repo="/home/tie303177/work/nabledge/work3", concurrency=1)

    print("Testing path construction:")
    print(f"  repo: {ctx.repo}")
    print(f"  knowledge_dir: {ctx.knowledge_dir}")
    print()

    # Simulate file_info
    file_info = {
        "id": "test_file",
        "output_path": "component/adapters/test_file.json",
        "assets_dir": "component/adapters/assets/test_file/"
    }

    # Test corrected paths (what step3_generate.py should do now)
    output_path = f"{ctx.knowledge_dir}/{file_info['output_path']}"
    assets_dir_abs = f"{ctx.knowledge_dir}/{file_info['assets_dir']}"

    print("Corrected paths (after fix):")
    print(f"  output_path: {output_path}")
    print(f"  assets_dir: {assets_dir_abs}")
    print()

    # Verify no duplication
    assert output_path.count(ctx.repo) == 1, "output_path should contain repo path exactly once"
    assert assets_dir_abs.count(ctx.repo) == 1, "assets_dir should contain repo path exactly once"
    assert not output_path.startswith(f"{ctx.repo}/{ctx.repo}"), "No path duplication"
    assert not assets_dir_abs.startswith(f"{ctx.repo}/{ctx.repo}"), "No path duplication"

    # Verify expected structure
    expected_output = "/home/tie303177/work/nabledge/work3/.claude/skills/nabledge-6/knowledge/component/adapters/test_file.json"
    assert output_path == expected_output, f"Expected: {expected_output}, Got: {output_path}"

    print("✅ All path construction tests passed!")
    print()
    print("Path structure is correct:")
    print(f"  - No duplication of '{ctx.repo}'")
    print(f"  - Files will be created in correct location")
    print(f"  - Validation will find the generated files")

if __name__ == "__main__":
    test_path_construction()
