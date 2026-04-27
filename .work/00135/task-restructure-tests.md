# タスク: knowledge-creator テストコード整理

## 目的

テストコードがアドホックに散在しており、メンテナンス負荷に対して品質向上に貢献していない。テスト方針を定め、あるべき構成に再編する。

## 結論

run.pyにkcコマンドのファサード関数を追加し、kc.shとE2Eテストの両方がファサード経由で実行する。E2Eテストは `tests/e2e/test_e2e.py` に集約。ユニットテストは `tests/ut/` 配下に整理する。

## 前提

- ブランチ: `120-generate-all-nabledge6-knowledge-files`
- 作業ディレクトリ: `tools/knowledge-creator/`

## 作業ルール

- 各Stepの終わりに `cd tools/knowledge-creator && python -m pytest tests/ -x -q` を実行し、全件passを確認してから次に進む
- failしたら次のStepに進まず原因を修正する

## 作業手順

Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6 → Step 7 → Step 8

---

### Step 0: テストルールを knowledge-creator.md に追記

`.claude/rules/knowledge-creator.md` の末尾に以下を追記する。
もし `.claude/rules/knowledge-creator-tests.md` が存在する場合は `git rm` で削除する。

追記内容:

```markdown

## テストコード方針

### 原則

- テストは品質向上に役立つ最小限だけ書く
- E2Eテストで主要フローをカバーし、ユニットテストはE2Eでカバーされない複雑なロジックにだけ書く

### テスト構成

    tests/
    ├── e2e/                     # E2E テスト
    │   ├── test_e2e.py          # kcコマンド用途別テスト（1ファイル）
    │   ├── conftest.py          # TestContext, _make_cc_mock 等
    │   └── generate_expected.py # 期待値の独立生成
    └── ut/                      # ユニットテスト
        ├── conftest.py          # 共通fixture（ctx, mock_claude, load_fixture）
        ├── fixtures/            # テストデータ
        ├── mode/                # --testモード用ファイル
        └── test_<module>.py

### E2Eテスト（tests/e2e/test_e2e.py）

- kcコマンドの用途（gen / gen --resume / regen --target / fix / fix --target）ごとにテストを作る
- run.py のファサード関数（kc_gen / kc_fix 等）を呼ぶ。phase文字列を手書きしない
- CCをモックにしており、出力はすべて決定的。完全一致でアサートする
- ファイル数などの数量もアサートする
- CCの呼び出し回数はコスト影響大なので、想定する呼び出し回数でアサートする
- TestContext で全出力先をlog_dir配下にリダイレクトする

### ユニットテスト（tests/ut/）

- E2Eでは検証しにくい複雑なロジックだけをピンポイントでテストする
- 書くべきもの: split判定、マージ、バリデーションルール、リンク解決、境界値、E2Eで通らない異常系
- 書かなくてよいもの: Contextプロパティ、単純な委譲、E2E正常系でカバーされるもの
```

テスト実行:
```bash
cd tools/knowledge-creator && python -m pytest tests/ -x -q
```

---

### Step 1: run.py にファサード関数を追加し、kc.sh から呼ぶ

#### 1-1. _run_pipeline の抽出

main() の for ループ内のパイプライン実行部分を `_run_pipeline(ctx, args)` として抽出する。

抽出範囲: `effective_target = args.target` の行から `_publish_reports(ctx, report)` の行まで。

main() は以下の構造になる:

```python
def main():
    args = parser.parse_args()
    # ...validation, logger setup, banner...
    for v in versions:
        ctx = Context(...)
        _run_pipeline(ctx, args)
```

#### 1-2. ファサード関数の追加

`_run_pipeline` の直前に以下を追加する:

```python
def kc_gen(ctx):
    """kc gen: 全件生成（Phase ABCDEM）。"""
    _run_pipeline(ctx, _make_args(ctx))


def kc_regen_target(ctx, targets):
    """kc regen --target: 指定ファイル再生成。"""
    _run_pipeline(ctx, _make_args(ctx, phase="ABCDEM", clean_phase="BD", target=targets))


def kc_fix(ctx):
    """kc fix: 品質改善。"""
    _run_pipeline(ctx, _make_args(ctx, phase="ACDEM", clean_phase="D"))


def kc_fix_target(ctx, targets):
    """kc fix --target: 指定ファイル品質改善。"""
    _run_pipeline(ctx, _make_args(ctx, phase="ACDEM", clean_phase="D", target=targets))


def _make_args(ctx, phase=None, clean_phase=None, target=None, regen=False):
    """ファサード用のargs構築。"""
    import argparse
    return argparse.Namespace(
        version=ctx.version,
        phase=phase,
        concurrency=ctx.concurrency,
        dry_run=False,
        test=ctx.test_file,
        max_rounds=ctx.max_rounds,
        clean_phase=clean_phase,
        target=target,
        yes=True,
        regen=regen,
        run_id=ctx.run_id,
        verbose=ctx.verbose,
    )
```

#### 1-3. main() に --command 引数を追加

main() の argparse に `--command` 引数を追加する:

```python
parser.add_argument("--command", type=str, default=None,
                    choices=["gen", "regen", "fix"],
                    help="kc command (used by kc.sh)")
```

main() のパイプライン実行部分を、`--command` 指定時はファサード関数にディスパッチする:

```python
if args.command:
    # kc.sh 経由: ファサード関数にディスパッチ
    if args.command == "gen":
        kc_gen(ctx)
    elif args.command == "regen":
        if args.target:
            kc_regen_target(ctx, args.target)
        else:
            # regen without target uses --regen flag (git pull flow)
            _run_pipeline(ctx, args)
    elif args.command == "fix":
        if args.target:
            kc_fix_target(ctx, args.target)
        else:
            kc_fix(ctx)
else:
    # 直接実行: 従来通り
    _run_pipeline(ctx, args)
```

#### 1-4. kc.sh を --command 経由に変更

kc.sh の各コマンドで `--command` を追加し、`--phase` / `--clean-phase` の手書きを削除する。

変更前:
```bash
gen)
    if [ "$RESUME" = true ]; then
        echo "🔄 中断再開モード"
        $PYTHON "$TOOL_DIR/scripts/run.py" --version "$VERSION" $PASSTHROUGH_ARGS
    else
        echo "🚀 全件生成モード"
        $PYTHON "$TOOL_DIR/scripts/clean.py" --version "$VERSION" ${YES_FLAG:---yes}
        $PYTHON "$TOOL_DIR/scripts/run.py" --version "$VERSION" $PASSTHROUGH_ARGS
    fi
    ;;
regen)
    if [ -n "$TARGET_ARGS" ]; then
        echo "🔄 特定ファイル再生成"
        $PYTHON "$TOOL_DIR/scripts/run.py" --version "$VERSION" \
            --phase ABCDEM --clean-phase BD $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
    else
        echo "🔄 ソース変更検知 → 再生成"
        $PYTHON "$TOOL_DIR/scripts/run.py" --version "$VERSION" \
            --regen ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
    fi
    ;;
fix)
    echo "🔧 品質改善モード"
    $PYTHON "$TOOL_DIR/scripts/run.py" --version "$VERSION" \
        --phase ACDEM --clean-phase D $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
    ;;
```

変更後:
```bash
gen)
    if [ "$RESUME" = true ]; then
        echo "🔄 中断再開モード"
        $PYTHON "$TOOL_DIR/scripts/run.py" --command gen --version "$VERSION" $PASSTHROUGH_ARGS
    else
        echo "🚀 全件生成モード"
        $PYTHON "$TOOL_DIR/scripts/clean.py" --version "$VERSION" ${YES_FLAG:---yes}
        $PYTHON "$TOOL_DIR/scripts/run.py" --command gen --version "$VERSION" $PASSTHROUGH_ARGS
    fi
    ;;
regen)
    if [ -n "$TARGET_ARGS" ]; then
        echo "🔄 特定ファイル再生成"
        $PYTHON "$TOOL_DIR/scripts/run.py" --command regen --version "$VERSION" \
            $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
    else
        echo "🔄 ソース変更検知 → 再生成"
        $PYTHON "$TOOL_DIR/scripts/run.py" --command regen --version "$VERSION" \
            ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
    fi
    ;;
fix)
    echo "🔧 品質改善モード"
    $PYTHON "$TOOL_DIR/scripts/run.py" --command fix --version "$VERSION" \
        $TARGET_ARGS ${YES_FLAG:---yes} $PASSTHROUGH_ARGS
    ;;
```

#### 1-5. test_kc_sh.py を更新

test_kc_sh.py のアサーションを `--command` 引数に合わせて更新する。

例: TestFixCommand.test_fix_uses_phase_cdem_and_clean_d

変更前:
```python
assert "--phase ACDEM" in cmd
assert "--clean-phase D" in cmd
```

変更後:
```python
assert "--command fix" in cmd
```

テスト実行:
```bash
cd tools/knowledge-creator && python -m pytest tests/ -x -q
```

---

### Step 2: E2Eテストをファサード呼び出しに変更

`tests/test_cache_separation.py` を変更する。

#### 2-1. _run_main を _run_with_mock に置き換え

既存の `_run_main` 関数（72行目〜）を削除し、以下に置き換える:

```python
from run import kc_gen, kc_regen_target, kc_fix, kc_fix_target, _run_pipeline, _make_args

def _run_with_mock(facade_fn, ctx, mock_fn, **kwargs):
    """ファサード関数をCCモック付きで呼ぶ。"""
    from unittest.mock import patch
    with patch("phase_b_generate._default_run_claude", mock_fn), \
         patch("phase_d_content_check._default_run_claude", mock_fn), \
         patch("phase_e_fix._default_run_claude", mock_fn):
        facade_fn(ctx, **kwargs)


def _run_phase_a_only(ctx, mock_fn):
    """テストセットアップ用: Phase Aのみ実行。"""
    args = _make_args(ctx, phase="A")
    from unittest.mock import patch
    with patch("phase_b_generate._default_run_claude", mock_fn), \
         patch("phase_d_content_check._default_run_claude", mock_fn), \
         patch("phase_e_fix._default_run_claude", mock_fn):
        _run_pipeline(ctx, args)
```

#### 2-2. 各呼び出しの変更

ファイル内の `_run_main` 呼び出しを以下の通り全て変更する:

```
_run_main(ctx, mock)
→ _run_with_mock(kc_gen, ctx, mock)

_run_main(ctx, mock, phases="A")
→ _run_phase_a_only(ctx, mock)

_run_main(ctx, mock, phases="ABCDEM", target=target_base_names, clean_phase="BD")
→ _run_with_mock(kc_regen_target, ctx, mock, targets=target_base_names)

_run_main(ctx, mock, phases="CDEM")
→ _run_with_mock(kc_fix, ctx, mock)

_run_main(ctx, mock, phases="CDEM", target=target_base_names, clean_phase="D")
→ _run_with_mock(kc_fix_target, ctx, mock, targets=target_base_names)
```

#### 2-3. 不要になったimportの削除

`_run_main`で使っていた以下のimportが不要になったら削除する:
- `from unittest.mock import patch, MagicMock`（_run_with_mockで使うのでpatchは残す）
- argparse関連

テスト実行:
```bash
cd tools/knowledge-creator && python -m pytest tests/test_cache_separation.py -x -q
```

---

### Step 3: ディレクトリ構成を作成

```bash
mkdir -p tests/e2e
mkdir -p tests/ut
touch tests/e2e/__init__.py
touch tests/ut/__init__.py
```

---

### Step 4: E2E関連ファイルを tests/e2e/ に移動

```bash
git mv tests/test_cache_separation.py tests/e2e/test_e2e.py
git mv tests/generate_expected.py tests/e2e/generate_expected.py
```

`tests/e2e/test_e2e.py` のdocstringを変更する:

変更前:
```python
"""E2E tests verifying cache separation between knowledge_cache_dir and knowledge_dir.

Key invariants:
- Phase B writes to knowledge_cache_dir, NOT knowledge_dir
- Phase C/D/E read from knowledge_cache_dir
- Phase M reads from knowledge_cache_dir, writes to knowledge_dir (delete-insert)
- After Phase M, catalog.json is restored to split state
"""
```

変更後:
```python
"""E2E tests for kc commands (gen / gen --resume / regen --target / fix / fix --target).

Tests call run.py facade functions (kc_gen, kc_fix, etc.) with mocked CC.
CCの出力は決定的なので、最終出力の完全一致・ファイル数・CC呼び出し回数でアサートする。
Expected values are computed by generate_expected.py independently from kc source code.
"""
```

`tests/e2e/test_e2e.py` 内のimportパスを修正する:
- `from generate_expected import ...` → パスが同じディレクトリなので変更不要
- `sys.path.insert` のパスを確認し、必要なら修正

`tests/e2e/conftest.py` を作成する:
```python
import sys, os
# scripts/ のモジュールを参照するため
TOOL_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TOOL_DIR, "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

テスト実行:
```bash
cd tools/knowledge-creator && python -m pytest tests/e2e/ -x -q
```

---

### Step 5: UTファイルを tests/ut/ に移動

既存の `tests/conftest.py` を `tests/ut/conftest.py` に移動する:

```bash
git mv tests/conftest.py tests/ut/conftest.py
```

`tests/ut/conftest.py` のFIXTURES_DIRパスを修正する:

変更前:
```python
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
```

変更後:
```python
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
```
（fixtures/もut/に移動するので変更不要）

fixtures/ と mode/ を ut/ に移動する:

```bash
git mv tests/fixtures tests/ut/fixtures
git mv tests/mode tests/ut/mode
```

テストファイルを移動する:

```bash
git mv tests/test_kc_sh.py tests/ut/test_kc_sh.py
git mv tests/test_cleaner.py tests/ut/test_cleaner.py
git mv tests/test_excel_classification.py tests/ut/test_excel_classification.py
git mv tests/test_index_rst_id.py tests/ut/test_index_rst_id.py
git mv tests/test_merge.py tests/ut/test_merge.py
git mv tests/test_no_knowledge_content.py tests/ut/test_no_knowledge_content.py
git mv tests/test_phase_c.py tests/ut/test_phase_c.py
git mv tests/test_phase_g.py tests/ut/test_phase_g.py
git mv tests/test_phase_m.py tests/ut/test_phase_m.py
git mv tests/test_rst_all_inclusive.py tests/ut/test_rst_all_inclusive.py
git mv tests/test_split_criteria.py tests/ut/test_split_criteria.py
git mv tests/test_unmatched_error.py tests/ut/test_unmatched_error.py
git mv tests/test_knowledge_meta.py tests/ut/test_knowledge_meta.py
git mv tests/test_e2e_regen.py tests/ut/test_e2e_regen.py
git mv tests/test_test_mode.py tests/ut/test_test_mode.py
```

各ファイルを残す理由（E2Eでカバーされない点）:

| ファイル | E2Eでカバーされない理由 |
|---|---|
| test_kc_sh | kc.shの引数→run.pyの引数変換。E2Eはrun.pyファサードから |
| test_phase_c | S1〜S16バリデーション個別ルール。E2Eは正常系のみ |
| test_split_criteria | 分割判定の境界値22テスト。純粋関数 |
| test_merge | splitマージのエッジケース（不完全part、non-split混在等） |
| test_phase_g | リンク解決の正規表現パターン別テスト |
| test_phase_m | merge→resolve→docsのRST解決個別パターン、assetパス |
| test_cleaner | target指定時のartifactリスト生成 |
| test_index_rst_id | index.rstのID生成境界値 |
| test_excel_classification | Excel分類パターンの分岐 |
| test_no_knowledge_content | no_knowledge_contentフラグの異常系 |
| test_rst_all_inclusive | _static除外、index.rst包含 |
| test_unmatched_error | unmatchedなRSTでSystemExit |
| test_knowledge_meta | git操作を含むregen変更検知。E2Eは`regen`未使用 |
| test_e2e_regen | regenフロー（git pull→変更検知→再生成）。同上 |
| test_test_mode | --testオプションのPhase Aフィルタリング。E2Eは`test=None`固定 |

テスト実行:
```bash
cd tools/knowledge-creator && python -m pytest tests/ -x -q
```

---

### Step 6: 不要テストファイル削除

```bash
git rm tests/test_e2e_split.py         # Phase直接呼び出しのB→M。TestGenでカバー
git rm tests/test_pipeline.py          # Phase直接呼び出しのB→F。TestGenでカバー
git rm tests/test_run_flow.py          # Phase直接呼び出しのB→E。TestGenでカバー
git rm tests/test_split_validation.py  # Phase C/D/Eのsplit。TestGenが全split IDでテスト
git rm tests/test_verification_loop.py # D→E→Cループ。TestGenのmax_rounds=2でカバー
git rm tests/test_run_phases.py        # main()経由のphase制御。ファサードでカバー
git rm tests/test_run_id.py            # Contextプロパティ19テスト
git rm tests/test_verbose.py           # --verbose機能テスト
git rm tests/test_target_filter.py     # TestRegenTarget/TestFixTargetでカバー
```

tests/直下に残っている `tests/__init__.py` 以外のファイルがないことを確認:

```bash
ls tests/*.py
# __init__.py のみであること
```

テスト実行:
```bash
cd tools/knowledge-creator && python -m pytest tests/ -x -q
```

---

### Step 7: 最終検証

**1. 全テストpass**:
```bash
cd tools/knowledge-creator && python -m pytest tests/ -x -q
```

**2. テストファイル構成の確認**:
```bash
find tests -type f -name "*.py" | sort
```

期待する構成:
```
tests/__init__.py
tests/e2e/__init__.py
tests/e2e/conftest.py
tests/e2e/generate_expected.py
tests/e2e/test_e2e.py
tests/ut/__init__.py
tests/ut/conftest.py
tests/ut/test_cleaner.py
tests/ut/test_e2e_regen.py
tests/ut/test_excel_classification.py
tests/ut/test_index_rst_id.py
tests/ut/test_kc_sh.py
tests/ut/test_knowledge_meta.py
tests/ut/test_merge.py
tests/ut/test_no_knowledge_content.py
tests/ut/test_phase_c.py
tests/ut/test_phase_g.py
tests/ut/test_phase_m.py
tests/ut/test_rst_all_inclusive.py
tests/ut/test_split_criteria.py
tests/ut/test_test_mode.py
tests/ut/test_unmatched_error.py
```

**3. 削除ファイルが存在しないこと**:
```bash
for f in test_cache_separation.py test_e2e_split.py test_pipeline.py test_run_flow.py test_split_validation.py test_verification_loop.py test_run_phases.py test_run_id.py test_verbose.py test_target_filter.py conftest.py generate_expected.py test_kc_sh.py; do
  test -f "tests/$f" && echo "ERROR: tests/$f still exists" || echo "OK: $f moved or deleted"
done
```

**4. ファサード関数の存在確認**:
```bash
grep -n "^def kc_gen\|^def kc_fix\|^def kc_regen\|^def kc_fix_target\|^def _run_pipeline\|^def _make_args" scripts/run.py
```

**5. kc.sh が --command を使っていること**:
```bash
grep "\-\-command" kc.sh
```

---

### Step 8: コミット

```bash
git add -A tools/knowledge-creator/ .claude/rules/knowledge-creator.md
git status
git commit -m "refactor: add kc facade functions and restructure tests

run.py:
- Extract _run_pipeline() from main()
- Add facade: kc_gen(), kc_regen_target(), kc_fix(), kc_fix_target()
- Add --command arg: kc.sh dispatches via --command instead of --phase

kc.sh:
- Use --command gen/regen/fix instead of --phase/--clean-phase

Tests:
- E2E: tests/e2e/test_e2e.py calls facade functions with mocked CC
- UT: 15 files moved to tests/ut/
- Deleted: 9 redundant test files
- .claude/rules/knowledge-creator.md updated with test policy

Fixes: TestFix/TestFixTarget now correctly use Phase ACDEM via kc_fix()
(was CDEM, missing Phase A)."
```
