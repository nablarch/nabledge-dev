# Design: Duplicate File ID Detection and Fix

**Issue**: #145
**Date**: 2026-03-07

## 問題：Phase B で SKIP が発生する

Phase B (`phase_b_generate.py`) の `generate_one` は、出力ファイルの存在チェックで生成をスキップする。
これは再実行時のインクリメンタル処理のための仕組みである。

```python
# phase_b_generate.py:147
if os.path.exists(output_path):
    self.logger.info(f"  [SKIP] {file_id}")
    return {"status": "skip", "id": file_id}
```

出力パスは `{knowledge_dir}/{type}/{category}/{file_id}.json` で決まる。
**2つのソースファイルが同じ `file_id` を持つと、同じ `output_path` になる。**
1ファイル目が生成された後、2ファイル目がそのパスの存在を検知して SKIP される。
エラーにはならず、カバレッジが静かに欠落する。

## 根本原因：ID生成がファイル名とカテゴリだけに依存

`generate_id`（`step2_classify.py:147`）が生成するIDは基本的に `{category}-{filename}` である。
ディレクトリ情報は使われない（`index.rst` の特殊処理を除く）。

```python
return f"{category}-{base_name}"
# base_name = 拡張子を除いたファイル名
```

同じカテゴリに分類される複数のサブディレクトリに、同名の RST ファイルが存在すると重複が生じる。

## 実際に重複しているファイル（v6 ソース全体）

調査の結果、以下の10個の重複IDと21ファイルが確認された。

| 重複ID | 件数 | 原因パターン |
|--------|------|-------------|
| `about-nablarch-application_framework` | 2 | index.rst のパターン basename 衝突 |
| `libraries-functional_comparison` | 3 | libraries/ 内の同名ファイル |
| `libraries-permission_check` | 2 | libraries/ 内の同名ファイル |
| `testing-framework-batch` | 2 | 02_RequestUnitTest/ vs 03_DealUnitTest/ |
| `testing-framework-delayed_receive` | 2 | 同上 |
| `testing-framework-delayed_send` | 2 | 同上 |
| `testing-framework-http_send_sync` | 2 | 同上 |
| `testing-framework-real` | 2 | 同上 |
| `testing-framework-rest` | 2 | 同上 |
| `testing-framework-send_sync` | 2 | 同上 |

フルパス：

```
about-nablarch-application_framework
  .lw/.../application_framework/index.rst
  .lw/.../application_framework/application_framework/index.rst

libraries-functional_comparison
  .lw/.../libraries/data_io/functional_comparison.rst
  .lw/.../libraries/validation/functional_comparison.rst
  .lw/.../libraries/database/functional_comparison.rst

libraries-permission_check
  .lw/.../libraries/permission_check.rst
  .lw/.../libraries/authorization/permission_check.rst

testing-framework-{batch,delayed_receive,delayed_send,http_send_sync,real,rest,send_sync}
  .lw/.../05_UnitTestGuide/02_RequestUnitTest/{name}.rst
  .lw/.../05_UnitTestGuide/03_DealUnitTest/{name}.rst
```

## 後方互換の制約

すでに知識ファイルの生成を開始している。
既存の生成済みファイルは現行のIDで保存されている（例：`libraries-functional_comparison.json`）。

ID を変更すると：
- 旧IDのファイルが孤立する（参照されなくなる）
- 新IDのファイルとして再生成が必要になる

**このため、既存の生成済みIDは変更しないことを優先する。**

## 設計の選択肢

### 案A：重複を全件リネームする（初期実装、リバート済み）

`_resolve_duplicate_ids` で重複を検出し、全件をパスベースIDに差し替える。

```
libraries-functional_comparison (3件すべて)
  → libraries-data-io-functional_comparison
  → libraries-validation-functional_comparison
  → libraries-database-functional_comparison
```

**問題**：生成済みの `libraries-functional_comparison.json` が孤立する。
後方互換が崩れる。

### 案B：「最初の1件はIDを据え置き、残りだけリネーム」

重複グループのうち最初の1件はIDを変えず、2件目以降だけ新IDにする。

**問題**：「最初」はファイルシステムの走査順に依存し非決定的。
実行環境によって結果が変わる可能性がある。

### 案C：RST_MAPPING にパスを追加して明示的に分類（推奨候補）

重複しているファイルに対して、より具体的なパターンを `RST_MAPPING` に追加し、
別のカテゴリに分類することで衝突を回避する。

```python
# 例: testing_framework の 03_DealUnitTest を別カテゴリにする
("development_tools/testing_framework/guide/.../03_DealUnitTest/", "development-tools", "testing-framework-deal"),
```

**利点**：
- 既存IDは一切変えない（後方互換を完全に保つ）
- ロジックが単純で見通しがよい（マッピングを追加するだけ）
- 特別な後処理が不要

**課題**：
- 対象ファイルを正確に把握してマッピングを書く必要がある
- 新カテゴリ名を適切に決める必要がある

### 案D：generate_id の基本ロジックを変更（全ファイル対象）

`generate_id` を `{category}-{dir}-{filename}` 形式にする。

**問題**：全IDが変わるため、後方互換が完全に崩れる。対象外。

## 対応方針（未確定、要議論）

案C（RST_MAPPING への明示追加）を基本方針として検討する。

- 既存の生成済みIDを変えない
- 新規ファイル（これまで SKIP されていた側）にのみ新しいカテゴリIDが付く
- ロジックの追加がなく、マッピングテーブルの変更だけで済む

合わせて、重複IDをテストで検出する仕組みは案Cに依らず有効なので、
テストは別途追加する（ただし実装は案Cの後で行う）。

## 次のステップ

- [ ] 案Cのカテゴリ設計を具体化する（どの名前にするか）
- [ ] RST_MAPPING への追加内容を決定する
- [ ] 追加後に重複ゼロを確認するテストを追加する
