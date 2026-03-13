# Task: 品質評価機能の追加

Issue: #191
Branch: `191-kc-final-eval`

## セットアップ

```bash
cd /home/claude && git clone https://github.com/nablarch/nabledge-dev.git
cd nabledge-dev
git fetch origin 191-kc-final-eval
git checkout 191-kc-final-eval
git reset --hard origin/main
```

## Step 0: test_test_mode.py を e2e に移動

`test_test_mode.py` は `.lw/nab-official/`（公式リポジトリのローカルワーキングコピー）に依存しており、クローン直後の環境では必ず失敗する。外部リソース依存のテストは UT ではなく e2e に属する。

```bash
cd tools/knowledge-creator
git mv tests/ut/test_test_mode.py tests/e2e/test_test_mode.py
```

### ベースライン確認（ゲート0）

```bash
python -m pytest tests/ut/ -q --tb=no
```

期待出力（末尾）: `170 passed`

失敗が 0 件であることを確認する。

### コミット

```bash
git add -A && git commit -m "fix: move test_test_mode.py from ut/ to e2e/

These tests depend on .lw/nab-official/ (real repository working copy)
which does not exist in CI/clone environments. They belong in e2e/.

Part of #191"
```

---

## Step 1: Phase C の validate_structure 戻り値変更 + A1〜A3

### 1-1. テストファイル作成

`tests/ut/test_phase_c_additional.py` を以下の内容で新規作成:

```python
"""Test additional Phase C checks (A1-A3)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from phase_c_structure_check import PhaseCStructureCheck


def _make_checker():
    return PhaseCStructureCheck.__new__(PhaseCStructureCheck)


class TestHintsMinimum:

    def test_hints_below_3_returns_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "テスト"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        a1 = [w for w in warnings if w.startswith("A1:")]
        assert len(a1) == 1
        assert "s1" in a1[0]

    def test_hints_3_or_more_no_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "B", "テスト"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        assert len([w for w in warnings if w.startswith("A1:")]) == 0


class TestHintsJapanese:

    def test_no_japanese_returns_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["Handler", "Config", "Setup"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        assert len([w for w in warnings if w.startswith("A2:")]) == 1

    def test_with_japanese_no_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["Handler", "ハンドラ", "Config"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        assert len([w for w in warnings if w.startswith("A2:")]) == 0


class TestFileSizeAnomaly:

    def test_too_small_returns_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "B", "テスト"]}],
            "sections": {"s1": "x" * 100}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge, separators=(',', ':')))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        a3 = [w for w in warnings if w.startswith("A3:")]
        if os.path.getsize(str(json_path)) < 300:
            assert len(a3) == 1

    def test_normal_size_no_warning(self, tmp_path):
        knowledge = {
            "id": "test", "title": "T", "no_knowledge_content": False,
            "official_doc_urls": ["https://example.com"],
            "index": [{"id": "s1", "title": "S", "hints": ["A", "B", "テスト"]}],
            "sections": {"s1": "x" * 500}
        }
        json_path = tmp_path / "test.json"
        json_path.write_text(json.dumps(knowledge, indent=2))
        source_path = tmp_path / "test.rst"
        source_path.write_text("Title\n=====\nContent\n")
        errors, warnings = _make_checker().validate_structure(str(json_path), str(source_path), "rst")
        a3 = [w for w in warnings if w.startswith("A3:")]
        if os.path.getsize(str(json_path)) >= 300:
            assert len(a3) == 0
```

### 1-2. RED 確認（ゲート1a）

```bash
python -m pytest tests/ut/test_phase_c_additional.py -q --tb=line 2>&1 | tail -1
```

期待: `6 failed`

### 1-3. 実装: scripts/phase_c_structure_check.py

#### (A) 早期 return の変更

対象箇所の確認:
```bash
grep -n "return \[f\"S1\|return errors$" scripts/phase_c_structure_check.py
```

5箇所の `return` を変更:
- `return [f"S1: ...]` → `return [f"S1: ...], []`
- 3箇所の `return errors` → `return errors, []`
- 最後の `return errors`（メソッド末尾）→ 削除して下記 (B) で置き換え

#### (B) メソッド末尾の `return errors` を以下で置き換え

```python
        # --- Additional quality checks (warnings, not errors) ---
        warnings = []

        # A1: Hints minimum count
        for entry in knowledge.get("index", []):
            if len(entry.get("hints", [])) < 3:
                warnings.append(f"A1: Section '{entry['id']}' has only {len(entry.get('hints', []))} hints (minimum: 3)")

        # A2: Hints Japanese presence
        for entry in knowledge.get("index", []):
            hints = entry.get("hints", [])
            has_japanese = any(
                any('\u3000' <= c <= '\u9fff' or '\uf900' <= c <= '\ufaff' for c in h)
                for h in hints
            )
            if not has_japanese:
                warnings.append(f"A2: Section '{entry['id']}' hints contain no Japanese")

        # A3: File size anomaly
        file_size = os.path.getsize(json_path)
        if file_size < 300:
            warnings.append(f"A3: File size {file_size}B is too small (< 300B)")
        elif file_size > 50 * 1024:
            warnings.append(f"A3: File size {file_size}B is too large (> 50KB)")

        return errors, warnings
```

#### (C) run() メソッド変更

results dict の初期化に追加: `"warning_count": 0, "warnings": {},`

`errs = self.validate_structure(...)` → `errs, warns = self.validate_structure(...)`

if errs ブロックの後に追加:
```python
            if warns:
                results["warnings"][fi["id"]] = warns
                results["warning_count"] += len(warns)
```

### 1-4. 既存テスト修正

```bash
sed -i 's/errors = PhaseCStructureCheck(ctx).validate_structure/errors, _ = PhaseCStructureCheck(ctx).validate_structure/g' tests/ut/test_phase_c.py tests/ut/test_no_knowledge_content.py
```

test_phase_c.py の `test_valid_passes` を手動変更:

変更前: `assert PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst") == []`

変更後:
```python
        errors, warnings = PhaseCStructureCheck(ctx).validate_structure(jp, sp, "rst")
        assert errors == []
        assert any("A2" in w for w in warnings)
```

### 1-5. GREEN + 回帰確認（ゲート1b）

```bash
python -m pytest tests/ut/test_phase_c_additional.py tests/ut/test_phase_c.py tests/ut/test_no_knowledge_content.py -q --tb=short 2>&1 | tail -1
```

期待: `22 passed`

```bash
python -m pytest tests/ut/ -q --tb=no 2>&1 | tail -1
```

期待: `176 passed`

### 1-6. コミット

```bash
git add -A && git commit -m "feat: add quality checks A1-A3 to Phase C

A1: hints minimum count (< 3 = warning)
A2: hints Japanese presence (no CJK = warning)
A3: file size anomaly (< 300B or > 50KB = warning)

validate_structure returns (errors, warnings) tuple.

Part of #191"
```

---

## Step 2: 最終検証の追加

### 2-1. テストファイル作成

`tests/ut/test_final_verification.py` を以下の内容で新規作成:

```python
"""Test final verification after CDE loop."""
import json
import os
import subprocess
import shutil
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))


def _setup_ctx_with_knowledge(tmp_path):
    """テスト用の Context + catalog + source + knowledge を準備する。"""
    from run import Context
    ctx = Context(version='6', repo=str(tmp_path), concurrency=1, max_rounds=2)
    os.makedirs(ctx.cache_dir, exist_ok=True)
    catalog = {
        "generated_at": "2026-01-01T00:00:00Z", "sources": [],
        "files": [{
            "id": "test-handler", "source_path": "src/test.rst",
            "format": "rst", "type": "component", "category": "handlers",
            "output_path": "component/handlers/test-handler.json",
        }]
    }
    with open(ctx.classified_list_path, 'w') as f:
        json.dump(catalog, f)
    os.makedirs(os.path.dirname(f"{ctx.repo}/src/test.rst"), exist_ok=True)
    with open(f"{ctx.repo}/src/test.rst", 'w') as f:
        f.write("Title\n=====\n\nContent here.\n")
    kdir = f"{ctx.knowledge_cache_dir}/component/handlers"
    os.makedirs(kdir, exist_ok=True)
    knowledge = {
        "id": "test-handler", "title": "Test Handler", "no_knowledge_content": False,
        "official_doc_urls": ["https://example.com"],
        "index": [{"id": "s1", "title": "Content", "hints": ["TestHandler", "テスト", "設定"]}],
        "sections": {"s1": "Content here with enough characters to pass minimum length check."}
    }
    with open(f"{kdir}/test-handler.json", 'w') as f:
        json.dump(knowledge, f)
    prompts_dir = os.path.join(ctx.repo, "tools/knowledge-creator/prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    real_prompts = os.path.join(os.path.dirname(__file__), '../../prompts')
    if os.path.exists(real_prompts):
        for fn in os.listdir(real_prompts):
            shutil.copy(os.path.join(real_prompts, fn), os.path.join(prompts_dir, fn))
    return ctx


class TestFinalVerification:

    def test_phase_c_only(self, tmp_path):
        """Phase C のみ指定 → phase_c 結果が返り、round = max_rounds + 1。"""
        from run import _run_final_verification
        ctx = _setup_ctx_with_knowledge(tmp_path)
        result = _run_final_verification(ctx, max_rounds=2, phases="C")
        assert result["round"] == 3
        assert result["phase_c"]["total"] == 1
        assert result["phase_c"]["pass"] == 1

    def test_phase_cd_clean(self, tmp_path):
        """C→D 実行。Phase D が clean を返す場合、has_issues == 0。"""
        from run import _run_final_verification
        ctx = _setup_ctx_with_knowledge(tmp_path)

        mock_findings = {"file_id": "test-handler", "status": "clean", "findings": []}

        def mock_cc(prompt, json_schema=None, log_dir=None, file_id=None, **kw):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(mock_findings, ensure_ascii=False), stderr=""
            )

        with patch("phase_d_content_check._default_run_claude", mock_cc):
            result = _run_final_verification(ctx, max_rounds=2, phases="CD")

        assert result["round"] == 3
        assert "phase_c" in result
        assert "phase_d" in result
        assert result["phase_d"]["has_issues"] == 0

    def test_phase_cd_with_findings(self, tmp_path):
        """C→D 実行。Phase D が findings を返す場合、findings が集計される。"""
        from run import _run_final_verification
        ctx = _setup_ctx_with_knowledge(tmp_path)

        mock_findings = {
            "file_id": "test-handler", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical",
                 "location": "s1", "description": "Missing warning"}
            ]
        }

        def mock_cc(prompt, json_schema=None, log_dir=None, file_id=None, **kw):
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(mock_findings, ensure_ascii=False), stderr=""
            )

        with patch("phase_d_content_check._default_run_claude", mock_cc):
            result = _run_final_verification(ctx, max_rounds=2, phases="CD")

        assert result["phase_d"]["has_issues"] == 1
        assert result["phase_d"]["findings"]["total"] >= 1
```

### 2-2. RED 確認（ゲート2a）

```bash
python -m pytest tests/ut/test_final_verification.py -q --tb=line 2>&1 | tail -1
```

期待: `3 failed`

### 2-3. 実装: scripts/run.py

#### (A) _run_final_verification 関数を追加

挿入位置の確認:
```bash
grep -n "^def _aggregate_findings" scripts/run.py
```

その行の直前に以下を挿入:

```python
def _run_final_verification(ctx, max_rounds, phases):
    """最終検証: CDE ループ後に C→D を 1 回実行。E（修正）は呼ばない。"""
    logger = get_logger()
    final_round = max_rounds + 1
    logger.info(f"\n📋Final Verification (Round {final_round})")

    result = {"round": final_round}

    c_result = None
    if "C" in phases:
        logger.info("\n✅Phase C: Structure Check (Final)")
        from phase_c_structure_check import PhaseCStructureCheck
        c_result = PhaseCStructureCheck(ctx).run()
        result["phase_c"] = {
            "total": c_result.get("total", 0),
            "pass": c_result.get("pass", 0),
            "fail": c_result.get("error_count", 0),
        }

    if "D" in phases:
        logger.info("\n🔍Phase D: Content Check (Final)")
        from phase_d_content_check import PhaseDContentCheck
        pass_ids = c_result.get("pass_ids") if c_result else None
        d_result = PhaseDContentCheck(ctx, dry_run=False).run(
            target_ids=pass_ids, round_num=final_round
        )
        findings_summary = _aggregate_findings(ctx, round_num=final_round)
        result["phase_d"] = {
            "total": d_result.get("clean", 0) + len(d_result.get("issue_file_ids", [])),
            "clean": d_result.get("clean", 0),
            "has_issues": len(d_result.get("issue_file_ids", [])),
            "findings": findings_summary,
            "metrics": d_result.get("metrics"),
        }

    return result


```

#### (B) パイプラインに最終検証を挿入

挿入位置の確認:
```bash
grep -n "# Phase M" scripts/run.py
```

`# Phase M (replaces G+F in default flow)` の行の直前に挿入:

```python
    # Final Verification
    loop_ended_with_fix = (
        len(report.get("phase_e_rounds", [])) > 0
        and len(report.get("phase_e_rounds", [])) == len(report.get("phase_d_rounds", []))
    )
    if loop_ended_with_fix and "D" in phases:
        final_result = _run_final_verification(ctx, ctx.max_rounds, phases)
        report["final_verification"] = final_result

```

### 2-4. GREEN + 回帰確認（ゲート2b）

```bash
python -m pytest tests/ut/test_final_verification.py -q --tb=short 2>&1 | tail -1
```

期待: `3 passed`

```bash
python -m pytest tests/ut/ -q --tb=no 2>&1 | tail -1
```

期待: `179 passed`

### 2-5. コミット

```bash
git add -A && git commit -m "feat: add final verification (C→D) after CDE improvement loop

Run Phase C and D one more time after the last Phase E fix.
Skip when the loop ended with all-clean (no Phase E executed).

Part of #191"
```

---

## Step 3: Phase V 品質評価

### 3-1. テストファイル作成

`tests/ut/test_phase_v.py` を以下の内容で新規作成:

```python
"""Test Phase V: Quality Evaluation."""
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))


class TestFactCollection:

    def test_collect_findings_summary(self, tmp_path):
        from phase_v_evaluate import PhaseVEvaluate
        findings_dir = tmp_path / "phase-d" / "findings"
        findings_dir.mkdir(parents=True)
        (findings_dir / "handler-a_r1.json").write_text(json.dumps({
            "file_id": "handler-a", "status": "has_issues",
            "findings": [
                {"category": "omission", "severity": "critical", "location": "s1", "description": "X"},
                {"category": "hints_missing", "severity": "minor", "location": "s2", "description": "Y"}
            ]
        }))
        (findings_dir / "handler-a_r2.json").write_text(json.dumps({
            "file_id": "handler-a", "status": "has_issues",
            "findings": [{"category": "hints_missing", "severity": "minor", "location": "s2", "description": "Y"}]
        }))
        (findings_dir / "handler-a_r3.json").write_text(json.dumps({
            "file_id": "handler-a", "status": "has_issues",
            "findings": [{"category": "hints_missing", "severity": "minor", "location": "s2", "description": "Y"}]
        }))
        (findings_dir / "handler-b_r1.json").write_text(json.dumps({
            "file_id": "handler-b", "status": "clean", "findings": []
        }))
        summary = PhaseVEvaluate.collect_findings_summary(str(findings_dir), max_rounds=2)
        assert summary["rounds"][1]["total"] == 2
        assert summary["rounds"][1]["by_category"]["omission"] == 1
        assert summary["rounds"][2]["total"] == 1
        assert summary["rounds"][3]["total"] == 1
        assert summary["final"]["by_category"]["hints_missing"] == 1

    def test_cross_tabulate(self, tmp_path):
        from phase_v_evaluate import PhaseVEvaluate
        findings_dir = tmp_path / "phase-d" / "findings"
        findings_dir.mkdir(parents=True)
        (findings_dir / "handlers-test_r3.json").write_text(json.dumps({
            "file_id": "handlers-test", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical", "location": "s1", "description": "X"}]
        }))
        (findings_dir / "libraries-dao_r3.json").write_text(json.dumps({
            "file_id": "libraries-dao", "status": "has_issues",
            "findings": [{"category": "fabrication", "severity": "critical", "location": "s1", "description": "Y"}]
        }))
        catalog = {"files": [
            {"id": "handlers-test", "category": "handlers"},
            {"id": "libraries-dao", "category": "libraries"},
        ]}
        cross = PhaseVEvaluate.cross_tabulate(str(findings_dir), catalog, final_round=3)
        assert cross["handlers"]["omission"] == 1
        assert cross["libraries"]["fabrication"] == 1

    def test_file_concentration(self, tmp_path):
        from phase_v_evaluate import PhaseVEvaluate
        findings_dir = tmp_path / "phase-d" / "findings"
        findings_dir.mkdir(parents=True)
        (findings_dir / "big-file_r3.json").write_text(json.dumps({
            "file_id": "big-file", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical",
                          "location": f"s{i}", "description": f"X{i}"} for i in range(5)]
        }))
        (findings_dir / "small-file_r3.json").write_text(json.dumps({
            "file_id": "small-file", "status": "has_issues",
            "findings": [{"category": "omission", "severity": "critical", "location": "s1", "description": "X"}]
        }))
        concentration = PhaseVEvaluate.file_concentration(str(findings_dir), final_round=3, top_n=10)
        assert concentration[0]["file_id"] == "big-file"
        assert concentration[0]["count"] == 5
        assert concentration[1]["file_id"] == "small-file"


class TestPhaseVRun:

    def test_run_with_residual_findings(self, tmp_path):
        """残留 findings → evaluate_file → integrate_proposals の連携を検証。"""
        from run import Context
        from phase_v_evaluate import PhaseVEvaluate

        ctx = Context(version='6', repo=str(tmp_path), concurrency=1, max_rounds=2)
        os.makedirs(ctx.cache_dir, exist_ok=True)
        catalog = {
            "generated_at": "2026-01-01T00:00:00Z", "sources": [],
            "files": [{"id": "handler-a", "source_path": "src/handler.rst",
                        "format": "rst", "type": "component", "category": "handlers",
                        "output_path": "component/handlers/handler-a.json"}]
        }
        with open(ctx.classified_list_path, 'w') as f:
            json.dump(catalog, f)

        os.makedirs(f"{ctx.repo}/src", exist_ok=True)
        with open(f"{ctx.repo}/src/handler.rst", 'w') as f:
            f.write("Handler\n=======\n\nContent.\n")

        kdir = f"{ctx.knowledge_cache_dir}/component/handlers"
        os.makedirs(kdir, exist_ok=True)
        with open(f"{kdir}/handler-a.json", 'w') as f:
            json.dump({"id": "handler-a", "sections": {"s1": "content"}}, f)

        os.makedirs(ctx.findings_dir, exist_ok=True)
        with open(f"{ctx.findings_dir}/handler-a_r3.json", 'w') as f:
            json.dump({
                "file_id": "handler-a", "status": "has_issues",
                "findings": [{"category": "omission", "severity": "critical",
                              "location": "s1", "description": "Missing"}]
            }, f)

        prompts_dir = f"{ctx.repo}/tools/knowledge-creator/prompts"
        os.makedirs(prompts_dir, exist_ok=True)
        real_prompts = os.path.join(os.path.dirname(__file__), '../../prompts')
        for fn in os.listdir(real_prompts):
            shutil.copy(os.path.join(real_prompts, fn), os.path.join(prompts_dir, fn))

        eval_result = {
            "file_id": "handler-a", "user_impact": "high",
            "needs_improvement": True, "reason": "Critical omission",
            "findings_assessment": [{"category": "omission", "location": "s1",
                                     "impact": "high", "justification": "Missing warning"}]
        }
        integ_result = {
            "proposals": [{"title": "Fix handler warnings", "purpose": "Prevent wrong implementation",
                           "target_files": ["handler-a"], "user_impact": "Critical",
                           "body": "Add missing warnings"}]
        }
        call_count = {"evaluate": 0, "integrate": 0}

        def mock_v(prompt, json_schema=None, log_dir=None, file_id=None, **kw):
            schema_str = json.dumps(json_schema) if json_schema else ""
            if "findings_assessment" in schema_str:
                call_count["evaluate"] += 1
                output = eval_result
            else:
                call_count["integrate"] += 1
                output = integ_result
            return subprocess.CompletedProcess(
                args=["claude"], returncode=0,
                stdout=json.dumps(output, ensure_ascii=False), stderr=""
            )

        phase_v = PhaseVEvaluate(ctx, dry_run=False, run_claude_fn=mock_v)
        result = phase_v.run(final_round=3)

        assert result["fact_data"]["summary"]["final"]["total"] == 1
        assert call_count["evaluate"] == 1
        assert len(result["file_evaluations"]) == 1
        assert result["file_evaluations"][0]["user_impact"] == "high"
        assert call_count["integrate"] == 1
        assert result["proposals"]["proposals"][0]["title"] == "Fix handler warnings"

    def test_run_dry_run_skips_cc(self, tmp_path):
        """dry_run=True の場合、CC は呼ばれない。"""
        from run import Context
        from phase_v_evaluate import PhaseVEvaluate

        ctx = Context(version='6', repo=str(tmp_path), concurrency=1, max_rounds=2)
        os.makedirs(ctx.cache_dir, exist_ok=True)
        with open(ctx.classified_list_path, 'w') as f:
            json.dump({"generated_at": "2026-01-01T00:00:00Z", "sources": [], "files": []}, f)

        prompts_dir = f"{ctx.repo}/tools/knowledge-creator/prompts"
        os.makedirs(prompts_dir, exist_ok=True)
        real_prompts = os.path.join(os.path.dirname(__file__), '../../prompts')
        for fn in os.listdir(real_prompts):
            shutil.copy(os.path.join(real_prompts, fn), os.path.join(prompts_dir, fn))

        def should_not_be_called(**kw):
            raise AssertionError("CC should not be called in dry_run mode")

        phase_v = PhaseVEvaluate(ctx, dry_run=True, run_claude_fn=should_not_be_called)
        result = phase_v.run(final_round=3)

        assert result["file_evaluations"] == []
        assert result["proposals"] is None
```

### 3-2. RED 確認（ゲート3a）

```bash
python -m pytest tests/ut/test_phase_v.py -q --tb=line 2>&1 | tail -1
```

期待: `5 failed`

### 3-3. 実装ファイル作成

#### (A) `scripts/phase_v_evaluate.py` を以下の内容で新規作成:

```python
"""Phase V: Quality Evaluation

Collects findings data, runs CC sub-agents for user impact assessment,
and generates improvement proposals.
"""

import os
import json
import glob
from common import load_json, read_file, run_claude as _default_run_claude, write_json
from logger import get_logger

EVALUATE_SCHEMA = {
    "type": "object",
    "required": ["file_id", "user_impact", "needs_improvement", "reason", "findings_assessment"],
    "properties": {
        "file_id": {"type": "string"},
        "user_impact": {"type": "string", "enum": ["high", "medium", "low", "none"]},
        "needs_improvement": {"type": "boolean"},
        "reason": {"type": "string"},
        "findings_assessment": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["category", "location", "impact", "justification"],
                "properties": {
                    "category": {"type": "string"},
                    "location": {"type": "string"},
                    "impact": {"type": "string"},
                    "justification": {"type": "string"}
                }
            }
        }
    }
}

INTEGRATE_SCHEMA = {
    "type": "object",
    "required": ["proposals"],
    "properties": {
        "proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "purpose", "target_files", "user_impact", "body"],
                "properties": {
                    "title": {"type": "string"},
                    "purpose": {"type": "string"},
                    "target_files": {"type": "array", "items": {"type": "string"}},
                    "user_impact": {"type": "string"},
                    "body": {"type": "string"}
                }
            }
        }
    }
}


class PhaseVEvaluate:
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude = run_claude_fn or _default_run_claude
        self.logger = get_logger()
        self.evaluate_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/evaluate.md"
        )
        self.integrate_template = read_file(
            f"{ctx.repo}/tools/knowledge-creator/prompts/evaluate_integrate.md"
        )

    @staticmethod
    def collect_findings_summary(findings_dir, max_rounds):
        summary = {"rounds": {}, "final": None}
        final_round = max_rounds + 1
        for rn in range(1, final_round + 1):
            paths = glob.glob(os.path.join(findings_dir, f"*_r{rn}.json"))
            total = critical = minor = 0
            by_category = {}
            for path in paths:
                try:
                    data = json.load(open(path, 'r', encoding='utf-8'))
                except (json.JSONDecodeError, OSError):
                    continue
                for f in data.get("findings", []):
                    total += 1
                    if f.get("severity") == "critical":
                        critical += 1
                    else:
                        minor += 1
                    cat = f.get("category", "unknown")
                    by_category[cat] = by_category.get(cat, 0) + 1
            summary["rounds"][rn] = {
                "total": total, "critical": critical, "minor": minor,
                "by_category": by_category,
            }
        summary["final"] = summary["rounds"].get(final_round, {})
        return summary

    @staticmethod
    def cross_tabulate(findings_dir, catalog, final_round):
        file_category_map = {f["id"]: f.get("category", "unknown") for f in catalog.get("files", [])}
        cross = {}
        paths = glob.glob(os.path.join(findings_dir, f"*_r{final_round}.json"))
        for path in paths:
            try:
                data = json.load(open(path, 'r', encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                continue
            fid = data.get("file_id", "")
            file_cat = file_category_map.get(fid, "unknown")
            cross.setdefault(file_cat, {})
            for f in data.get("findings", []):
                cat = f.get("category", "unknown")
                cross[file_cat][cat] = cross[file_cat].get(cat, 0) + 1
        return cross

    @staticmethod
    def file_concentration(findings_dir, final_round, top_n=10):
        counts = []
        paths = glob.glob(os.path.join(findings_dir, f"*_r{final_round}.json"))
        for path in paths:
            try:
                data = json.load(open(path, 'r', encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                continue
            findings = data.get("findings", [])
            if findings:
                cats = [f.get("category", "") for f in findings]
                counts.append({
                    "file_id": data.get("file_id", ""),
                    "count": len(findings),
                    "categories": list(set(cats)),
                })
        counts.sort(key=lambda x: -x["count"])
        return counts[:top_n]

    def evaluate_file(self, file_id, findings, rst_content, json_content, d_logs, e_logs):
        prompt = self.evaluate_template
        prompt = prompt.replace("{FILE_ID}", file_id)
        prompt = prompt.replace("{FINDINGS}", json.dumps(findings, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{RST_CONTENT}", rst_content)
        prompt = prompt.replace("{JSON_CONTENT}", json_content)
        prompt = prompt.replace("{EXECUTION_LOGS}", f"--- Phase D logs ---\n{d_logs}\n--- Phase E logs ---\n{e_logs}")
        result = self.run_claude(
            prompt=prompt, json_schema=EVALUATE_SCHEMA,
            log_dir=f"{self.ctx.log_dir}/phase-v/evaluations", file_id=file_id,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None

    def integrate_proposals(self, file_evaluations, findings_summary):
        prompt = self.integrate_template
        prompt = prompt.replace("{FILE_EVALUATIONS}", json.dumps(file_evaluations, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{FINDINGS_SUMMARY}", json.dumps(findings_summary, ensure_ascii=False, indent=2))
        result = self.run_claude(
            prompt=prompt, json_schema=INTEGRATE_SCHEMA,
            log_dir=f"{self.ctx.log_dir}/phase-v/integration", file_id="integration",
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None

    def run(self, final_round):
        self.logger.info("\n📊Phase V: Quality Evaluation")
        catalog = load_json(self.ctx.classified_list_path)

        self.logger.info("   V1: Collecting findings summary...")
        summary = self.collect_findings_summary(self.ctx.findings_dir, self.ctx.max_rounds)
        cross = self.cross_tabulate(self.ctx.findings_dir, catalog, final_round)
        concentration = self.file_concentration(self.ctx.findings_dir, final_round)
        fact_data = {"summary": summary, "cross_tabulation": cross, "file_concentration": concentration}

        self.logger.info("   V2: Evaluating files with residual findings...")
        final_findings_paths = glob.glob(
            os.path.join(self.ctx.findings_dir, f"*_r{final_round}.json")
        )
        files_with_issues = []
        for path in final_findings_paths:
            data = load_json(path)
            if data.get("status") == "has_issues":
                files_with_issues.append(data)

        file_evaluations = []
        if not self.dry_run and files_with_issues:
            file_map = {f["id"]: f for f in catalog.get("files", [])}
            for fdata in files_with_issues:
                fid = fdata["file_id"]
                fi = file_map.get(fid)
                if not fi:
                    continue
                rst_path = f"{self.ctx.repo}/{fi['source_path']}"
                json_path = f"{self.ctx.knowledge_cache_dir}/{fi['output_path']}"
                rst_content = read_file(rst_path) if os.path.exists(rst_path) else ""
                json_content = read_file(json_path) if os.path.exists(json_path) else ""
                d_logs = self._read_latest_log(self.ctx.phase_d_executions_dir, fid)
                e_logs = self._read_latest_log(self.ctx.phase_e_executions_dir, fid)
                eval_result = self.evaluate_file(fid, fdata["findings"], rst_content, json_content, d_logs, e_logs)
                if eval_result:
                    eval_result["category"] = fi.get("category", "unknown")
                    file_evaluations.append(eval_result)

        proposals = None
        if not self.dry_run and file_evaluations:
            self.logger.info("   V3: Generating improvement proposals...")
            proposals = self.integrate_proposals(file_evaluations, fact_data)

        result = {"fact_data": fact_data, "file_evaluations": file_evaluations, "proposals": proposals}
        os.makedirs(f"{self.ctx.log_dir}/phase-v", exist_ok=True)
        write_json(f"{self.ctx.log_dir}/phase-v/result.json", result)
        return result

    def _read_latest_log(self, executions_dir, file_id):
        if not os.path.exists(executions_dir):
            return ""
        logs = sorted(glob.glob(os.path.join(executions_dir, f"{file_id}_*.json")), reverse=True)
        if not logs:
            return ""
        try:
            data = load_json(logs[0])
            return json.dumps(data, ensure_ascii=False, indent=2)[:5000]
        except Exception:
            return ""
```

#### (B) `prompts/evaluate.md` を以下の内容で新規作成:

```markdown
You are a quality evaluator for Nablarch knowledge files used by AI agents in mission-critical enterprise system development.

## Context

Nabledge provides AI agents with Nablarch framework knowledge. The knowledge files are the ONLY information source for the agent.

## Task

Evaluate the following residual findings and determine their user impact.

## File: `{FILE_ID}`

### Residual Findings

```json
{FINDINGS}
```

### Source (RST)

```
{RST_CONTENT}
```

### Knowledge File (JSON)

```
{JSON_CONTENT}
```

### Improvement Loop Logs

{EXECUTION_LOGS}

## Evaluation Criteria

For each finding, assess:
1. **User Impact**: high / medium / low / none
2. **Why it persisted**: Using the logs, explain why D→E did not resolve this.

## Output

Respond with JSON matching the provided schema.
Set `needs_improvement` to `true` if ANY finding has `high` or `medium` impact.
```

#### (C) `prompts/evaluate_integrate.md` を以下の内容で新規作成:

```markdown
You are creating improvement Issue proposals for the Nabledge knowledge file pipeline.

## Input: File-level Evaluations

```json
{FILE_EVALUATIONS}
```

## Input: Findings Summary

```json
{FINDINGS_SUMMARY}
```

## Task

Group files needing improvement by PURPOSE. For each group create an Issue proposal with title, purpose, target_files, user_impact, body (all in English).

Do NOT propose improvements for `needs_improvement: false` files.

## Output

Respond with JSON matching the provided schema.
```

### 3-4. GREEN + 回帰確認（ゲート3b）

```bash
python -m pytest tests/ut/test_phase_v.py -q --tb=short 2>&1 | tail -1
```

期待: `5 passed`

```bash
python -m pytest tests/ut/ -q --tb=no 2>&1 | tail -1
```

期待: `184 passed`

### 3-5. コミット

```bash
git add -A && git commit -m "feat: add Phase V quality evaluation with CC sub-agent proposals

V1: Script-based findings analysis (summary, cross-tabulation, concentration)
V2: CC sub-agent per-file user impact evaluation
V3: CC sub-agent integration and Issue proposal generation

Part of #191"
```

---

## Step 4: レポート拡張 + パイプライン統合 + e2e mock

### 4-1. テストファイル作成

`tests/ut/test_report_quality.py` を以下の内容で新規作成:

```python
"""Test quality evaluation section in reports."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))


class TestQualityReportSection:

    def test_render_includes_quality_section(self):
        from run import _render_summary_md, Context
        ctx = Context.__new__(Context)
        ctx.run_id = "test"
        ctx.max_rounds = 2
        report = {
            "meta": {"run_id": "test", "version": "6", "phases": "BCDEMV",
                     "max_rounds": 2, "concurrency": 4, "test_mode": False,
                     "started_at": "2026-01-01T00:00:00Z",
                     "finished_at": "2026-01-01T01:00:00Z",
                     "duration_sec": 3600},
            "phase_d_rounds": [], "phase_e_rounds": [],
            "final_verification": {
                "round": 3,
                "phase_c": {"total": 10, "pass": 10, "fail": 0},
                "phase_d": {"total": 10, "clean": 8, "has_issues": 2,
                            "findings": {"total": 3, "critical": 1, "minor": 2,
                                         "by_category": {"omission": 1, "hints_missing": 2}}},
            },
            "quality_evaluation": {
                "fact_data": {"summary": {"rounds": {
                    1: {"total": 10, "critical": 5, "minor": 5, "by_category": {"omission": 5, "hints_missing": 5}},
                    2: {"total": 6, "critical": 2, "minor": 4, "by_category": {"omission": 2, "hints_missing": 4}},
                    3: {"total": 3, "critical": 1, "minor": 2, "by_category": {"omission": 1, "hints_missing": 2}},
                }, "final": {"total": 3}}},
                "proposals": {"proposals": [{
                    "title": "Fix missing warnings", "purpose": "Prevent wrong implementation",
                    "target_files": ["handler-a"], "user_impact": "Critical", "body": "Details"}]},
            },
        }
        md = _render_summary_md(ctx, report, [])
        assert "品質評価" in md
        assert "改善提案" in md
        assert "omission" in md

    def test_render_without_quality_evaluation(self):
        from run import _render_summary_md, Context
        ctx = Context.__new__(Context)
        ctx.run_id = "test"
        ctx.max_rounds = 2
        report = {
            "meta": {"run_id": "test", "version": "6", "phases": "BCD",
                     "max_rounds": 2, "concurrency": 4, "test_mode": False,
                     "started_at": "2026-01-01T00:00:00Z",
                     "finished_at": "2026-01-01T01:00:00Z",
                     "duration_sec": 3600},
            "phase_d_rounds": [], "phase_e_rounds": [],
        }
        md = _render_summary_md(ctx, report, [])
        assert "品質評価" not in md
```

### 4-2. RED 確認（ゲート4a）

```bash
python -m pytest tests/ut/test_report_quality.py -q --tb=line 2>&1 | tail -1
```

期待: `1 failed, 1 passed`

### 4-3. 実装

#### (A) _render_summary_md にセクション追加

挿入位置の確認:
```bash
grep -n "lines.append(f'---')" scripts/run.py
```

`_render_summary_md` 内の `lines.append(f'---')` の直前に以下を挿入:

```python
    # Final Verification
    fv = report.get("final_verification")
    if fv:
        lines.append(f'## 最終検証 (Round {fv.get("round", "?")})')
        lines.append(f'')
        fv_c = fv.get("phase_c") or {}
        if fv_c:
            lines.append(f'**Phase C**: {fv_c.get("pass", 0)}/{fv_c.get("total", 0)} pass, '
                         f'{fv_c.get("fail", 0)} fail')
            lines.append(f'')
        fv_d = fv.get("phase_d") or {}
        if fv_d:
            lines.append(f'**Phase D**: {fv_d.get("clean", 0)}/{fv_d.get("total", 0)} clean, '
                         f'{fv_d.get("has_issues", 0)} has_issues')
            fv_f = fv_d.get("findings") or {}
            if fv_f.get("total", 0) > 0:
                lines.append(f'')
                lines.append(f'| 指標 | 値 |')
                lines.append(f'|--------|-------|')
                lines.append(f'| 指摘事項 合計 | {fv_f.get("total", 0)} |')
                lines.append(f'| 指摘事項 重大 | {fv_f.get("critical", 0)} |')
                lines.append(f'| 指摘事項 軽微 | {fv_f.get("minor", 0)} |')
                by_cat = fv_f.get("by_category") or {}
                if by_cat:
                    lines.append(f'| カテゴリ別 | {", ".join(f"{k}:{v}" for k,v in by_cat.items())} |')
            lines.append(f'')

    # Quality Evaluation
    qe = report.get("quality_evaluation")
    if qe:
        lines.append(f'## 品質評価')
        lines.append(f'')
        fd = qe.get("fact_data", {})
        summary = fd.get("summary", {})
        rounds_data = summary.get("rounds", {})
        if rounds_data:
            lines.append(f'### findings 推移')
            lines.append(f'')
            round_nums = sorted(rounds_data.keys())
            headers = ['指標'] + [f'R{rn}' if rn <= ctx.max_rounds else '最終検証' for rn in round_nums]
            lines.append('| ' + ' | '.join(str(h) for h in headers) + ' |')
            lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
            for metric in ['total', 'critical', 'minor']:
                row = [metric]
                for rn in round_nums:
                    row.append(str(rounds_data[rn].get(metric, 0)))
                lines.append('| ' + ' | '.join(row) + ' |')
            all_cats = set()
            for rn_data in rounds_data.values():
                all_cats.update(rn_data.get("by_category", {}).keys())
            for cat in sorted(all_cats):
                row = [cat]
                for rn in round_nums:
                    row.append(str(rounds_data[rn].get("by_category", {}).get(cat, 0)))
                lines.append('| ' + ' | '.join(row) + ' |')
            lines.append(f'')
        proposals = qe.get("proposals", {}).get("proposals", []) if qe.get("proposals") else []
        if proposals:
            lines.append(f'### 改善提案')
            lines.append(f'')
            for i, p in enumerate(proposals, 1):
                lines.append(f'#### 提案 {i}: {p.get("title", "")}')
                lines.append(f'')
                lines.append(f'**目的**: {p.get("purpose", "")}')
                lines.append(f'')
                lines.append(f'**ユーザーインパクト**: {p.get("user_impact", "")}')
                lines.append(f'')
                lines.append(f'**対象ファイル**: {", ".join(p.get("target_files", []))}')
                lines.append(f'')
```

#### (B) パイプラインに Phase V 呼び出し追加

挿入位置の確認:
```bash
grep -n "finished_at = datetime" scripts/run.py
```

その行の直前に挿入:

```python
    # Phase V: Quality Evaluation
    if "V" in phases and report.get("final_verification"):
        from phase_v_evaluate import PhaseVEvaluate
        final_round = report["final_verification"]["round"]
        v_result = PhaseVEvaluate(ctx, dry_run=args.dry_run).run(final_round=final_round)
        report["quality_evaluation"] = v_result
```

#### (C) デフォルト phases 変更

```bash
grep -n '"ABCDEM"' scripts/run.py
```

`_run_pipeline` 内の `args.phase or "ABCDEM"` の行のみ変更: `"ABCDEM"` → `"ABCDEMV"`
`kc_regen_target` の `phase="ABCDEM"` は変更しない。

#### (D) banner 表示

```bash
grep -n "ABCDEM (all)" scripts/run.py
```

`'ABCDEM (all)'` → `'ABCDEMV (all)'`

#### (E) kc_gen docstring

```bash
grep -n "Phase ABCDEM" scripts/run.py
```

`Phase ABCDEM` → `Phase ABCDEMV`

#### (F) e2e mock 修正

```bash
grep -n "phase_e_fix._default_run_claude" tests/e2e/test_e2e.py
```

出力される 2 箇所の各行を変更:

変更前:
```python
         patch("phase_e_fix._default_run_claude", mock_fn):
```

変更後:
```python
         patch("phase_e_fix._default_run_claude", mock_fn), \
         patch("phase_v_evaluate._default_run_claude", mock_fn):
```

### 4-4. GREEN + 回帰確認（ゲート4b）

```bash
python -m pytest tests/ut/test_report_quality.py -q --tb=short 2>&1 | tail -1
```

期待: `2 passed`

```bash
python -m pytest tests/ut/ -q --tb=no 2>&1 | tail -1
```

期待: `186 passed`

### 4-5. コミット

```bash
git add -A && git commit -m "feat: add quality evaluation section to reports

- Render final verification and findings trend in report
- Add Phase V call to pipeline (after Phase M)
- Default phases: ABCDEMV
- Add Phase V mock to e2e test helpers

Part of #191"
```

---

## 最終確認（ゲート5）

```bash
python -m pytest tests/ut/ -q --tb=no 2>&1 | tail -1
```

期待: `186 passed`

失敗が 0 件であることを確認する。

```bash
git log --oneline origin/main..HEAD
```

期待: 5 コミット（Step 0〜4）

## push

```bash
git push origin 191-kc-final-eval --force-with-lease
```
