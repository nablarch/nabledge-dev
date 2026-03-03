# 分割ファイル対応パイプライン改修タスク

## 背景と目的

現行のknowledge-creatorパイプラインでは、大きなソースファイルを分割してPhase B（生成）を行い、Phase Bの最後に`_merge_split_files()`でマージしてから後続の検証フェーズに渡している。

### 不具合: libraries-tagのマージ失敗

**発生した問題:** libraries-tag（4パート、合計40セクション）でマージ後にセクションが3つに減少。

**原因の特定（実行ログの全フェーズ分析）:**

1. Phase B: 4パート正常生成（15+9+14+2 = 40セクション、合計72,022 chars）
2. Phase B末尾の`_merge_split_files`: 40セクションのJSONに正常マージ
3. Phase D: マージ済み`libraries-tag`をチェック → 2件のomissionを検出
4. **Phase E: マージ済みJSONを修正依頼 → effective_input=608,260トークン（ctx=200Kの3.04倍）→ 3セクションしか返らなかった**
5. Phase Eが3セクションの出力でファイル全体を上書き → **37セクション消失**

**根本原因: 入力コンテキストオーバーフロー（出力上限ではない）**

Phase Eの実行ログを詳細に分析した結果、当初想定した「出力上限」ではなく「入力側のコンテキスト欠落」が真因であることが判明。

```
■ Phase E失敗（libraries-tag）
  eff_input=608,260  ctx=200,000  → 3.04倍超過
  out=43,181  turns=3  sections=3  index=40
  → indexは40エントリ保持（JSONヘッダ部、コンパクトで圧縮されにくい）
  → sectionsは3キーのみ（JSON後半の巨大オブジェクト、圧縮時に最初に削られる）

■ Phase E成功（libraries-tag_reference） - 比較対象
  eff_input=335,773  ctx=200,000  → 1.68倍超過
  out=63,151  turns=2  sections=65  index=65
  → 出力トークンはむしろtagより多い（63K > 43K）が全セクション保持
```

Claude Code CLIがeff_input > ctxの場合にコンテキスト圧縮を行い、知識JSONの後半部分が切り詰められた結果、Claudeには3セクション分しか「見えない」状態で修正版を生成したと判断される。

**全フェーズのログメトリクス:**

Phase B（生成、パート単位）:
```
tag-1: eff_in=146,779  out=22,397  turns=2  secs=15  chars=21,580  $1.21
tag-2: eff_in=293,890  out=38,423  turns=3  secs=9   chars=23,976  $1.96
tag-3: eff_in=142,112  out=22,662  turns=2  secs=14  chars=22,292  $1.08
tag-4: eff_in=121,427  out=17,452  turns=3  secs=2   chars=4,174   $0.67
```

Phase D（内容チェック、マージ後）:
```
tag:     eff_in=371,949  → 1.86x OVER  status=has_issues  findings=2
tag_ref: eff_in=185,950  → OK          status=has_issues  findings=12
adaptor: eff_in=216,485  → 1.08x OVER  status=clean
```

Phase E（修正、マージ後）:
```
tag:     eff_in=608,260  → 3.04x OVER  → FAIL (3/40 sections, 2,495 chars)
tag_ref: eff_in=335,773  → 1.68x OVER  → OK   (65/65 sections, 39,248 chars)
```

### 変更後のフロー

```
Phase B: 分割生成（現行通り、マージはしない）
      |
Phase C: 構造チェック（分割ファイル単位）
      |
Phase D: 内容チェック（分割ファイル単位）
      |
Phase E: 修正（分割ファイル単位）
      |
[C/D/Eループ完了、全パート OK]
      |
Phase M (新設): マージ + リンク解決 + 閲覧用MD生成
      |
完了
```

この設計であれば、Phase D/Eは常にパート単位のJSONを扱うため、eff_inputがPhase B生成時と同程度（120K〜180K）に収まり、コンテキストオーバーフローが構造的に発生しない。

ただし、現行の分割基準（`FILE_LINE_THRESHOLD=1000`, `SECTION_LINE_THRESHOLD=1000`）はRSTの行数ベースであり、生成後のknowledge JSONのサイズ（=Claude APIへの実効入力トークン数）を考慮していない。実際のログデータでは、1パートあたり chars=4,174〜40,361 と大きなばらつきがある。この問題への対応はTask 7で扱う。

---

## 現行コードの前提知識

### ファイル構成

```
tools/knowledge-creator/
  run.py                       # メインエントリ (Context, phase実行制御)
  steps/
    common.py                  # load_json, write_json, run_claude
    phase_b_generate.py        # 生成 + _merge_split_files()
    phase_c_structure_check.py # 構造チェック (S1-S15)
    phase_d_content_check.py   # 内容チェック (Claude使用)
    phase_e_fix.py             # 修正 (Claude使用)
    phase_f_finalize.py        # index.toon + 閲覧用MD + サマリ
    phase_g_resolve_links.py   # RST→Markdownリンク変換
  tests/
    conftest.py                # テストフィクスチャ, make_mock_run_claude
    test_phase_c.py            # Phase C単体テスト (8件 PASS)
    test_phase_g.py            # Phase G単体テスト (8件 PASS)
    test_pipeline.py           # パイプライン結合テスト (6件 FAIL)
```

### run_claude関数のシグネチャ

`steps/common.py`に定義:
```python
def run_claude(prompt: str, json_schema: dict, log_dir: str, file_id: str) -> subprocess.CompletedProcess:
```

全フェーズ（B/D/E）から同じキーワード引数パターンで呼ばれる:
```python
result = self.run_claude(
    prompt=prompt,
    json_schema=...,
    log_dir=self.ctx.phase_X_executions_dir,
    file_id=file_id
)
```

### 分割ファイルの仕組み

Step2Classifyが大きなソースを分割すると、classified.jsonに以下の構造で登録される:

```json
{
  "id": "libraries-tag-1",
  "split_info": {
    "is_split": true,
    "original_id": "libraries-tag",
    "part": 1,
    "total_parts": 4
  },
  "section_range": {
    "start_line": 0,
    "end_line": 500,
    "sections": ["概要", "基本的な使い方"]
  },
  "output_path": "component/libraries/libraries-tag-1.json"
}
```

### 現行の分割ロジック（Step2Classify）

`steps/step2_classify.py`に実装:

**判定基準（should_split_file）:**
```python
FILE_LINE_THRESHOLD = 1000     # ファイル全体がこの行数を超えたら分割
SECTION_LINE_THRESHOLD = 1000  # いずれかのh2セクションがこの行数を超えたら分割
```

**分割アルゴリズム（split_file_entry）:**
1. h2セクション一覧を取得
2. `SECTION_LINE_THRESHOLD`超のh2はh3に展開（サブセクション分割）
3. セクションをグループ化: 累計行数が`SECTION_LINE_THRESHOLD`超で新パートに分割
4. 各パートに`section_range`（start_line, end_line, sections）と`split_info`を付与

**問題点（ログデータから判明）:**
- RSTの行数のみで分割を判定しており、生成後のknowledge JSONサイズとの相関が弱い
- 実際のログデータでは、同じ程度の行数でも生成結果のcharsに大きなばらつき（4K〜40K）
- Phase E時のeff_inputは「ソース行数」だけでなく「生成済みknowledge JSON + ソース + プロンプト」の合計で決まる
- `adaptor-2`は6セクション・40,361 charsと、セクション数は少ないが生成結果が最大

### 既存の _merge_split_files()（Phase Bの末尾）

マージロジック自体は正常に動作している（sections結合、index統合、assets統合）。問題はマージ後の巨大ファイルがPhase D/Eに適さないこと。

`_merge_split_files`が参照するctxのプロパティ:
- `self.ctx.classified_list_path` — classified.jsonの読み書き
- `self.ctx.knowledge_dir` — knowledge JSONの読み書き、パートファイル削除

### RST source vs JSON output のサイズ比率（実績データ）

```
File                         RST chars  sec_cont  json_oh  JSON chars  cont/RST  JSON/RST
adapters-micrometer_adaptor     80,069    73,636   10,634      84,270    0.92x     1.05x
libraries-tag                   86,013    72,022   15,337      87,359    0.84x     1.02x
libraries-tag_reference        103,094    38,456   13,943      52,399    0.37x     0.51x
```

- **sec_cont** = sections内のテキスト合計。RSTマークアップが除去されるため必ずRSTより小さい（0.37x〜0.92x）
- **json_oh** = JSON構造のオーバーヘッド（index, hints, id, title, urls等）。10K〜15K chars程度で安定
- **JSON/RST** = JSON全体 / RST。sec_cont + json_ohの結果として0.51x〜1.05x

JSONが全体としてRSTと同等になるのは、セクション内容は縮むがJSON overhead（10K-15K）が加算されるため。
Phase Eの出力検証ガードレール（Task 2）では**section_chars同士を比較**するので、overheadの影響を受けない。

### 既存テストの状態

conftest.pyの`make_mock_run_claude`のシグネチャが古く（`log_dir`, `file_id`パラメータ未対応）、パイプラインテスト6件が全滅。Phase C単体テスト8件とPhase G単体テスト8件は全パス。

### 現行のPhase C/D/Eの処理パターン（変更箇所の理解に必要）

**Phase C** (`phase_c_structure_check.py`):
- `run()` → classified.jsonを読み、各ファイルの`validate_structure(json_path, source_path, format)`を呼ぶ
- S9チェック（80-86行目）: `count_source_headings()`でソース全体のヘディング数を数え、sections数と比較
- **分割ファイルの問題**: ソース全体のヘディング数 > パートのsections数 → 常にS9エラー

**Phase D** (`phase_d_content_check.py`):
- `check_one(file_info)` → 72行目: `source = read_file(source_path)` でソース全体を読み込み
- `_build_prompt(file_info, knowledge, source_content)` でプロンプトに全ソースを渡す
- **分割ファイルの問題**: パートのsectionsに対応しないソース部分も含まれ、不要なfindingsが出る

**Phase E** (`phase_e_fix.py`):
- `fix_one(file_info)` → 63行目: `source = read_file(source_path)` でソース全体を読み込み
- **分割ファイルの問題**: Phase Dと同じ

**Phase B** (`phase_b_generate.py`):
- `generate_one(file_info)` → 154-155行目: `section_range`がある場合は`_extract_section_range()`で切り出し済み
- **つまりPhase Bは既に分割対応済み**。Phase D/Eに同じパターンを適用すればよい

---

## タスク一覧

### Task 0: mock修正（前提タスク）

**目的:** 既存テストを動くようにする。後続タスクの前提。

**テストを先に書く:**
なし（既存テストがそのまま期待するテスト）。テストを実行して全て失敗を確認 → 修正 → 全パスを確認。

**実装:**
`tests/conftest.py`の`make_mock_run_claude`内の`mock_fn`シグネチャを修正:

```python
# Before (conftest.py 56行目)
def mock_fn(prompt, timeout=600, json_schema=None):

# After
def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
```

`run_claude`の実シグネチャは `run_claude(prompt, json_schema, log_dir, file_id)` であり、全フェーズ（B/D/E）がキーワード引数で呼ぶ。mockもこの4パラメータを受け取れればよい。`**kwargs`は将来の引数追加への安全弁。

**完了条件:** `pytest tests/ -v` で既存テスト全21件がパスすること。

---

### Task 1: Phase Bからマージ処理を分離

**目的:** `_merge_split_files()`をPhase Bから切り出し、独立した呼び出し可能なクラスにする。

**テストを先に書く:** `tests/test_merge.py`

```
TestMergeSplitFiles:
  test_merge_two_parts
    - 2パートの分割ファイル(knowledge JSON)を作成
    - マージ実行
    - 結果のJSONが正しくマージされていることを確認
      (sections結合、index統合、assets統合)
    - パートファイルが削除されていること
    - classified.jsonが更新されていること

  test_merge_skips_incomplete_parts
    - 3パートのうち2パートのみ存在
    - マージ実行
    - スキップされること（例外なし）

  test_no_split_files_noop
    - split_infoのないファイルのみ
    - マージ実行
    - 何も変更されないこと

  test_merge_preserves_non_split_files
    - split + non-splitが混在
    - マージ後、non-splitファイルがclassified.jsonに残っていること
```

**実装:**

1. `steps/merge.py` を新規作成。クラス名は`MergeSplitFiles`:

```python
class MergeSplitFiles:
    """Merge split knowledge files into single files."""
    def __init__(self, ctx):
        self.ctx = ctx
        # 使用するctxプロパティ:
        #   ctx.classified_list_path — classified.json読み書き
        #   ctx.knowledge_dir — knowledge JSONの読み書き、パート削除

    def run(self):
        # phase_b_generate.py の _merge_split_files() のロジックをそのまま移動
        ...
```

2. `phase_b_generate.py` から変更:

```python
# Before (367行目)
        if not self.dry_run:
            self._merge_split_files()

# After: この2行を削除（_merge_split_filesメソッド自体も削除）
```

**完了条件:** test_merge.pyの全テストがパスし、既存テスト21件もパスすること。

---

### Task 2: Phase C/D/Eで分割ファイルを直接扱えるようにする

**目的:** 分割ファイル（`libraries-tag-1.json`等）がPhase C/D/Eをそのまま通過できることを確認・修正する。

**テストを先に書く:** `tests/test_split_validation.py`

```
TestSplitFileStructureCheck:
  test_split_file_passes_structure_check
    - split_info付きのclassified.jsonエントリを作成
    - 対応するknowledge JSON（パート1）を作成
    - Phase C実行
    - エラーなしでパスすること

  test_split_file_s9_uses_section_range
    - ソース全体に4つのh2ヘディングがあるRSTファイル
    - パート1のknowledge JSONには2セクションだけ
    - section_range.sectionsも2エントリ
    - Phase C実行 → S9エラーにならないこと
    - （section_rangeなしの場合はS9エラーになることも確認）

TestSplitFileContentCheck:
  test_split_file_content_check_uses_section_range
    - Phase D実行時、run_claudeに渡されるprompt内のソース内容が
      section_rangeで切り出された範囲のみであること（mock検証）

TestSplitFileFix:
  test_split_file_fix_uses_section_range
    - Phase E実行時、run_claudeに渡されるprompt内のソース内容が
      section_rangeで切り出された範囲のみであること（mock検証）
```

**実装（3つのPhaseに対するBefore/After）:**

**Phase C** (`phase_c_structure_check.py`):

```python
# Before (run() 内、133行目)
errs = self.validate_structure(json_path, source_path, fi["format"])

# After: file_infoを渡すように変更
errs = self.validate_structure(json_path, source_path, fi["format"], fi)
```

```python
# Before (validate_structure シグネチャ、32行目)
def validate_structure(self, json_path, source_path, source_format):

# After: file_info引数を追加（デフォルトNoneで後方互換を維持）
def validate_structure(self, json_path, source_path, source_format, file_info=None):
```

```python
# Before (S9チェック、80-86行目)
# S9: Section count
if os.path.exists(source_path):
    source_content = read_file(source_path)
    expected = self.count_source_headings(source_content, source_format)
    actual = len(knowledge.get("sections", {}))
    if actual < expected:
        errors.append(f"S9: Section count {actual} < source headings {expected}")

# After: section_rangeがある場合はそちらのセクション数を期待値にする
# S9: Section count
if file_info and "section_range" in file_info:
    expected = len(file_info["section_range"]["sections"])
elif os.path.exists(source_path):
    source_content = read_file(source_path)
    expected = self.count_source_headings(source_content, source_format)
else:
    expected = 0
actual = len(knowledge.get("sections", {}))
if expected > 0 and actual < expected:
    errors.append(f"S9: Section count {actual} < source headings {expected}")
```

**Phase D** (`phase_d_content_check.py`):

```python
# Before (check_one内、71-73行目)
knowledge = load_json(json_path)
source = read_file(source_path)
prompt = self._build_prompt(file_info, knowledge, source)

# After: section_rangeがある場合はソースを切り出す
knowledge = load_json(json_path)
source = read_file(source_path)
if "section_range" in file_info:
    lines = source.splitlines()
    sr = file_info["section_range"]
    source = "\n".join(lines[sr["start_line"]:sr["end_line"]])
prompt = self._build_prompt(file_info, knowledge, source)
```

**Phase E** (`phase_e_fix.py`):

```python
# Before (fix_one内、62-63行目)
knowledge = load_json(f"{self.ctx.knowledge_dir}/{file_info['output_path']}")
source = read_file(f"{self.ctx.repo}/{file_info['source_path']}")

# After: section_rangeがある場合はソースを切り出す
knowledge = load_json(f"{self.ctx.knowledge_dir}/{file_info['output_path']}")
source = read_file(f"{self.ctx.repo}/{file_info['source_path']}")
if "section_range" in file_info:
    lines = source.splitlines()
    sr = file_info["section_range"]
    source = "\n".join(lines[sr["start_line"]:sr["end_line"]])
```

注: このソース切り出しパターンは`phase_b_generate.py`の`_extract_section_range()`（137-139行目）と同一ロジック。共通ユーティリティ化は任意（Phase B内にprivateメソッドとして既にあるため、common.pyに移すのが理想だが、各Phase内にインラインで書いても問題ない）。

**Phase E追加: 出力サイズ検証ガードレール** (`phase_e_fix.py`):

今回の不具合はPhase Eの出力が入力の3%に縮小したことで発生した。実データでのセクション内容（section_chars）の比率:

```
Phase E input vs output (section_chars comparison):
  tag:      0.03x ← 異常! (72,022 chars → 2,495 chars = 97%消失)
  tag_ref:  1.02x ← 正常  (38,456 chars → 39,248 chars = 微増)

参考: RST→JSON変換時のsection_chars/RST比率 (0.37x〜0.92x)
  → セクション内容自体は必ずRSTより縮む
  → Phase Eは「修正」なので、入力JSONと出力JSONのsection_charsはほぼ同一になるはず
```

Phase Eは「修正」なので、出力が入力より大幅に縮むことはあり得ない。`fix_one`内でサイズチェックを追加する:

```python
# After (fix_one内、fixedを書き込む前に追加、76行目付近)
if result.returncode == 0:
    fixed = json.loads(result.stdout)
    # Guard: output must not shrink drastically
    input_sec_chars = sum(len(v) for v in knowledge.get("sections", {}).values())
    output_sec_chars = sum(len(v) for v in fixed.get("sections", {}).values())
    if input_sec_chars > 0 and output_sec_chars < input_sec_chars * 0.5:
        print(f"    WARNING: {file_id}: output shrunk to {output_sec_chars/input_sec_chars:.0%} "
              f"({output_sec_chars:,} / {input_sec_chars:,} chars) - rejecting fix")
        return {"status": "error", "id": file_id,
                "error": f"Output too small: {output_sec_chars}/{input_sec_chars} chars"}
    if not self.dry_run:
        write_json(...)
```

閾値0.5x（50%未満で拒否）の根拠: 正常なPhase E出力は入力の1.0x前後（修正なので微増）。0.51xが最低の正常値（tag_ref）なので、50%未満なら確実に異常。

テストを追加:
```
TestSplitFileFix (test_split_validation.pyに追加):
  test_fix_rejects_drastically_shrunk_output
    - 入力: 10セクション、10,000 chars
    - mockが返す修正結果: 2セクション、500 chars（5%に縮小）
    - fix_one → status="error"、ファイルは上書きされないこと
```

**完了条件:** test_split_validation.pyと既存テスト全パス。

---

### Task 3: run.pyのフロー確認（変更は不要の可能性が高い）

**目的:** run.pyのC/D/Eループが分割ファイルのまま正しく動くことをテストで確認する。

**背景:** run.pyのC/D/Eループ（175-212行目）は以下の流れ:
1. Phase C → `c_result["pass_ids"]` を取得（= 構造チェックをpassしたファイルID一覧）
2. Phase D → `pass_ids`をtarget_idsとして渡し、issue_file_idsを取得
3. Phase E → `issue_file_ids`をtarget_idsとして渡す

分割ファイルのIDは`libraries-tag-1`等であり、上記のフィルタ処理はID文字列マッチなので**run.pyの変更なしで動く**。ただし、Task 1でPhase Bのマージを削除した後、run.pyがPhase Bの後でマージを試みないことの確認が必要。

**テストを先に書く:** `tests/test_run_flow.py`

```
TestRunFlowWithSplitFiles:
  test_phase_b_no_longer_merges
    - split_info付きclassified.jsonを用意
    - Phase Bをmockで実行（パートファイルを生成）
    - パートファイルがそのまま残っていること（マージされていないこと）

  test_split_ids_pass_through_cde_loop
    - split_info付きclassified.jsonを用意
    - パートファイルを配置
    - Phase C → D → E をmockで実行
    - 各パートのIDがC/D/Eを正しく通過していること
```

**実装:**
run.pyの変更は不要の見込み。テストが失敗した場合のみ修正する。

**完了条件:** test_run_flow.pyと既存テスト全パス。

---

### Task 4: Phase M（マージ → リンク解決 → 閲覧用MD）の新設

**目的:** C/D/Eループ完了後に実行する「仕上げ」フェーズを新設する。

**テストを先に書く:** `tests/test_phase_m.py`

```
TestPhaseM:
  test_merge_then_resolve_then_docs
    - 2パートの分割ファイルをknowledge_dirに配置
    - split_info付きclassified.jsonを用意
    - Phase M実行
    - マージ済みJSONが存在すること
    - パートJSONが削除されていること
    - classified.jsonが更新されていること
    - リンク解決済みファイルが存在すること（knowledge_resolved_dir）
    - 閲覧用MDが存在すること（docs_dir）
    - index.toonが存在すること

  test_phase_m_no_split_files
    - split_infoのないファイルのみ
    - Phase M実行
    - マージスキップ、リンク解決と閲覧用MD生成は実行されること

  test_phase_m_rst_links_resolved_in_merged
    - マージ後のJSONにRSTリンクが含まれるケース
    - Phase M実行後、resolved版でRSTリンクがMarkdownに変換されていること

  test_phase_m_asset_paths_in_docs
    - マージ後のJSON内のassetパスが
    - 閲覧用MDで正しい相対パスに変換されていること
```

**実装:**

`steps/phase_m_finalize.py` を新規作成:

```python
class PhaseMFinalize:
    """Phase M: Merge + Resolve Links + Generate Docs

    Post-validation finalization phase.
    1. Merge split files (from merge.py)
    2. Resolve RST links (from phase_g_resolve_links.py)
    3. Generate browsable docs + index (from phase_f_finalize.py)
    """
    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude_fn = run_claude_fn

    def run(self):
        from steps.merge import MergeSplitFiles
        from steps.phase_g_resolve_links import PhaseGResolveLinks
        from steps.phase_f_finalize import PhaseFFinalize

        MergeSplitFiles(self.ctx).run()
        PhaseGResolveLinks(self.ctx).run()
        PhaseFFinalize(self.ctx, dry_run=self.dry_run,
                       run_claude_fn=self.run_claude_fn).run()
```

**完了条件:** test_phase_m.pyと既存テスト全パス。

---

### Task 5: run.pyのフェーズ制御更新

**目的:** コマンドラインのphaseオプションにMを追加し、既存のG/Fフェーズ制御と整合させる。

**テストを先に書く:** `tests/test_run_phases.py`

```
TestPhaseControl:
  test_default_phases_include_m
    - --phaseなしで実行 → Phase Mが実行されること

  test_explicit_phase_m
    - --phase M で実行 → Phase Mのみ実行されること

  test_phase_bcdem_full_flow
    - --phase BCDEM → 全フローが正しい順序で実行されること

  test_backward_compat_gf_still_works
    - --phase GF → 従来のG→F順序で個別実行されること（後方互換）
```

**実装:**

run.pyの該当セクション（156行目以降）を以下のように変更:

```python
# Before (156行目)
phases = args.phase or "ABCDEFG"

# After
phases = args.phase or "ABCDEM"
```

```python
# Before (214-226行目: Phase G/Fブロック)
# Phase G
if "G" in phases:
    print("\n🔗Phase G: Resolve Links")
    ...
    PhaseGResolveLinks(ctx).run()

# Phase F
if "F" in phases:
    print("\n📦Phase F: Finalize")
    ...
    PhaseFFinalize(ctx, dry_run=args.dry_run).run()

# After: Phase Mブロックを追加し、G/Fは後方互換で残す
# Phase M (replaces G+F in default flow)
if "M" in phases:
    print("\n📦Phase M: Merge + Resolve + Finalize")
    print("   └─ Merging, resolving links, generating docs...")
    from steps.phase_m_finalize import PhaseMFinalize
    PhaseMFinalize(ctx, dry_run=args.dry_run).run()

# Phase G (backward compat: only when explicitly specified without M)
if "G" in phases and "M" not in phases:
    print("\n🔗Phase G: Resolve Links")
    print("   └─ Resolving RST cross-references...")
    from steps.phase_g_resolve_links import PhaseGResolveLinks
    PhaseGResolveLinks(ctx).run()

# Phase F (backward compat: only when explicitly specified without M)
if "F" in phases and "M" not in phases:
    print("\n📦Phase F: Finalize")
    print("   └─ Generating browsable docs and index...")
    from steps.phase_f_finalize import PhaseFFinalize
    PhaseFFinalize(ctx, dry_run=args.dry_run).run()
```

Phase表示も更新:
```python
# Before (144行目)
print(f"   Phases: {args.phase or 'ABCDEFG (all)'}")

# After
print(f"   Phases: {args.phase or 'ABCDEM (all)'}")
```

**完了条件:** test_run_phases.pyと既存テスト全パス。

---

### Task 6: 結合テスト（エンドツーエンド）

**目的:** 分割ファイルの生成から最終出力まで、全フローが正しく動くことを確認する。

**テストを先に書く:** `tests/test_e2e_split.py`

```
TestE2ESplitPipeline:
  test_full_pipeline_split_to_final
    - 2パート分割のclassified.jsonとソースファイルを用意
    - Phase B → C → D(clean) → M を実行
    - 最終出力を検証:
      - マージ済みknowledge JSONが正しい（全セクション含む）
      - リンク解決済み版が正しい
      - 閲覧用MDが正しい
      - index.toonに正しいエントリがある
      - パートファイルが存在しない

  test_full_pipeline_split_with_fix_cycle
    - Phase B → C → D(issues) → E(fix) → C → D(clean) → M
    - fixサイクルを1回通過して最終出力に到達すること
    - 全セクションが保持されていること（今回の不具合の再現防止）

  test_mixed_split_and_nonsplit
    - 分割ファイル + 通常ファイルの混在
    - 両方が正しく処理されて最終出力に含まれること
```

**mockのstate管理方針:**

`test_full_pipeline_split_with_fix_cycle`では、Phase Dの応答をラウンドごとに切り替える必要がある。以下のパターンでmockを構成する:

```python
def make_stateful_mock():
    """Phase Dの呼び出しカウンタでclean/has_issuesを切り替えるmock"""
    call_count = {"d": 0}

    def mock_fn(prompt, json_schema=None, log_dir=None, file_id=None, **kwargs):
        schema_str = json.dumps(json_schema) if json_schema else ""

        if "findings" in schema_str:
            # Phase D
            call_count["d"] += 1
            if call_count["d"] <= 2:  # 分割2パート分 = 最初のラウンド
                return mock_result({
                    "file_id": file_id,
                    "status": "has_issues",
                    "findings": [{"category": "omission", "severity": "minor",
                                  "location": "overview", "description": "test finding"}]
                })
            else:
                return mock_result({
                    "file_id": file_id,
                    "status": "clean",
                    "findings": []
                })
        elif "trace" in schema_str:
            # Phase B - 標準のknowledge返却
            return mock_result(generate_output)
        else:
            # Phase E - fixしたknowledge返却
            return mock_result(fix_output)

    return mock_fn
```

**実装:** テストのみ。全タスクの統合確認。

**完了条件:** test_e2e_split.pyと全テスト（既存+新規）がパスすること。

---

### Task 7: 分割基準の見直し（コンテキストオーバーフロー防止）

**目的:** 現行のRST行数ベースの分割基準を、Phase E実行時のeffective_inputが安全圏に収まるように改善する。

**背景（ログデータから導出した根拠）:**

Phase Bの実績データ:
```
tag-1: RST ~500行  eff_in=146,779  secs=15  chars=21,580  安全
tag-2: RST ~500行  eff_in=293,890  secs=9   chars=23,976  eff_in超過だがOK
tag-3: RST ~500行  eff_in=142,112  secs=14  chars=22,292  安全
tag-4: RST ~500行  eff_in=121,427  secs=2   chars=4,174   安全
adaptor-1: ~500行  eff_in=147,071  secs=8   chars=33,275  安全
adaptor-2: ~500行  eff_in=235,833  secs=6   chars=40,361  eff_in超過
```

Phase E時のeff_input構成:
```
eff_input = system_prompt(~10K) + source_rst + knowledge_json + findings + multi_turn_overhead
```

安全圏の目安:
- ctx=200,000トークン
- Phase Bで安定動作: eff_in < 150,000
- 分割後パイプライン（Task 2）ではPhase Eがパート単位のため、Phase B程度のeff_inに収まる

**現行基準の問題:**
```python
FILE_LINE_THRESHOLD = 1000     # ソースRST行数で判定
SECTION_LINE_THRESHOLD = 1000  # セクションRST行数 & グループ化上限（二重使用）
```
- 生成後のknowledge JSONサイズとの相関が弱い
- テーブル定義中心（tag: 平均1.4K chars/sec）と説明文中心（adaptor: 平均5.7K chars/sec）で約4倍異なる
- `SECTION_LINE_THRESHOLD`が「h3展開判定」と「グループ化上限」を兼務しており意味が不明瞭
- セクション数の上限がなく、多数の小セクションが1パートに集約される可能性あり

**テストを先に書く:** `tests/test_split_criteria.py`

```
TestSplitCriteria:
  test_file_under_threshold_not_split
    - 500行のRSTファイル、セクション5個
    - should_split_file -> False

  test_file_over_line_threshold_split
    - 1000行超のRSTファイル
    - should_split_file -> True

  test_file_with_many_sections_split
    - 600行のRSTファイル、セクション20個（行数は閾値以下）
    - should_split_file -> True（セクション数超過で分割）

  test_grouping_respects_line_limit
    - h2セクション10個（各150行 = 合計1500行）
    - split_file_entry -> 各パートが800行以下

  test_grouping_respects_section_count_limit
    - h2セクション20個（各30行 = 合計600行）
    - split_file_entry -> 各パートが15セクション以下

  test_grouping_splits_on_whichever_limit_hit_first
    - h2セクション12個（各100行 = 合計1200行）
    - 行数上限とセクション数上限の両方が守られていること

  test_large_section_expanded_to_h3
    - 1つのh2セクションが1000行超
    - h3サブセクションに展開されること

  test_single_oversized_h2_without_h3_stays_as_one_part
    - 1つのh2セクション1000行超、h3なし
    - 警告付きで1パートとして扱われること（現行動作を維持）
```

**実装:**

1. **閾値の調整と定数の分離** (`step2_classify.py` 104-106行目):

```python
# Before
class Step2Classify:
    FILE_LINE_THRESHOLD = 1000
    SECTION_LINE_THRESHOLD = 1000

# After
class Step2Classify:
    FILE_LINE_THRESHOLD = 800           # ファイル全体の分割判定
    GROUP_LINE_LIMIT = 800              # パートごとの累計行数上限
    GROUP_SECTION_LIMIT = 15            # パートごとのセクション数上限（新設）
    LARGE_SECTION_LINE_THRESHOLD = 800  # h3展開のための閾値
```

2. **should_split_fileにセクション数判定を追加** (248-257行目):

```python
# Before
file_exceeds = total_lines > self.FILE_LINE_THRESHOLD
has_large_section = any(s['line_count'] > self.SECTION_LINE_THRESHOLD for s in sections)
should_split = file_exceeds or has_large_section

# After
file_exceeds = total_lines > self.FILE_LINE_THRESHOLD
has_large_section = any(s['line_count'] > self.LARGE_SECTION_LINE_THRESHOLD for s in sections)
has_many_sections = len(sections) > self.GROUP_SECTION_LIMIT
should_split = file_exceeds or has_large_section or has_many_sections
```

3. **split_file_entryのh3展開閾値を分離** (278行目):

```python
# Before
if section['line_count'] > self.SECTION_LINE_THRESHOLD:

# After
if section['line_count'] > self.LARGE_SECTION_LINE_THRESHOLD:
```

4. **split_file_entryのグループ化ロジック改善** (304行目):

```python
# Before: 行数のみで判定
if current_group and (current_lines + section_lines > self.SECTION_LINE_THRESHOLD):

# After: 行数 OR セクション数で判定
if current_group and (
    current_lines + section_lines > self.GROUP_LINE_LIMIT
    or len(current_group) >= self.GROUP_SECTION_LIMIT
):
```

**閾値選定の根拠:**

| 基準 | 旧値 | 新値 | 根拠 |
|------|------|------|------|
| FILE_LINE_THRESHOLD | 1000行 | 800行 | 500行/パートでeff_in=120K-150Kに安定。800行でも余裕あり |
| GROUP_LINE_LIMIT | 1000行(兼務) | 800行(専用) | グループ化でも800行ならeff_in<180Kの見込み |
| GROUP_SECTION_LIMIT | なし | 15 | tag-1が15 secsでchars=21,580と安定 |
| LARGE_SECTION_LINE_THRESHOLD | 1000行(兼務) | 800行(専用) | h3展開判定を独立定数化 |

**完了条件:** test_split_criteria.pyと全テスト（既存+新規）がパスすること。

---

## 実行順序と依存関係

```
Task 0 (mock修正)
  |
Task 1 (マージ分離)
  |
Task 2 (C/D/Eの分割対応)
  |
Task 3 (run.pyフロー確認) ← run.py変更は不要の見込み。テストで確認のみ
  |
Task 4 (Phase M新設)
  |
Task 5 (フェーズ制御)
  |
Task 6 (結合テスト)
  |
Task 7 (分割基準見直し) ← Step2Classifyの変更のみ。パイプライン側は変更不要
```

## テストフィクスチャの追加（共通）

### conftest.pyに追加するフィクスチャ

```python
@pytest.fixture
def split_classified():
    """2パート分割のclassified.jsonデータ"""
    return {
        "version": "6",
        "generated_at": "2026-01-01T00:00:00Z",
        "files": [
            {
                "id": "libraries-tag-1",
                "source_path": "tests/fixtures/sample_source_split.rst",
                "format": "rst",
                "filename": "sample_source_split.rst",
                "type": "component",
                "category": "libraries",
                "output_path": "component/libraries/libraries-tag-1.json",
                "assets_dir": "component/libraries/assets/libraries-tag-1/",
                "split_info": {
                    "is_split": True,
                    "original_id": "libraries-tag",
                    "part": 1,
                    "total_parts": 2
                },
                "section_range": {
                    "start_line": 0,
                    "end_line": 30,
                    "sections": ["概要"]
                }
            },
            {
                "id": "libraries-tag-2",
                "source_path": "tests/fixtures/sample_source_split.rst",
                "format": "rst",
                "filename": "sample_source_split.rst",
                "type": "component",
                "category": "libraries",
                "output_path": "component/libraries/libraries-tag-2.json",
                "assets_dir": "component/libraries/assets/libraries-tag-2/",
                "split_info": {
                    "is_split": True,
                    "original_id": "libraries-tag",
                    "part": 2,
                    "total_parts": 2
                },
                "section_range": {
                    "start_line": 30,
                    "end_line": 60,
                    "sections": ["モジュール一覧"]
                }
            }
        ]
    }
```

### tests/fixtures/ に追加するファイル

**`sample_source_split.rst`** — 2セクション、60行程度のRST:
```rst
.. _tag-label:

タグライブラリ
==========================================

概要
-----

タグライブラリの概要。

.. important::
   タグは必ずJSPファイル内で使用すること。

（以下、30行目まで概要セクションの内容）

モジュール一覧
---------------

.. code-block:: xml

   <dependency>
     <groupId>com.nablarch.framework</groupId>
     <artifactId>nablarch-fw-web-tag</artifactId>
   </dependency>

（以下、60行目までモジュールセクションの内容）
```

**`sample_split_part1.json`** — パート1のknowledge JSON:
```json
{
  "id": "libraries-tag-1",
  "title": "タグライブラリ",
  "official_doc_urls": [
    "https://nablarch.github.io/docs/LATEST/doc/application_framework/libraries/tag.html"
  ],
  "index": [
    {
      "id": "overview",
      "title": "概要",
      "hints": ["タグライブラリ", "JSP", "カスタムタグ"]
    }
  ],
  "sections": {
    "overview": "タグライブラリの概要。\n\n> **重要**: タグは必ずJSPファイル内で使用すること。"
  }
}
```

**`sample_split_part2.json`** — パート2のknowledge JSON:
```json
{
  "id": "libraries-tag-2",
  "title": "タグライブラリ",
  "official_doc_urls": [
    "https://nablarch.github.io/docs/LATEST/doc/application_framework/libraries/tag.html"
  ],
  "index": [
    {
      "id": "module-list",
      "title": "モジュール一覧",
      "hints": ["nablarch-fw-web-tag", "dependency"]
    }
  ],
  "sections": {
    "module-list": "```xml\n<dependency>\n  <groupId>com.nablarch.framework</groupId>\n  <artifactId>nablarch-fw-web-tag</artifactId>\n</dependency>\n```"
  }
}
```
