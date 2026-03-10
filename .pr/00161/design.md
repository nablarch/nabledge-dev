# Design: PR#161 - Phase C structural validation failures fix

**Related Issue**: #150
**PR**: #161
**Branch**: `150-fix-phase-c-failures`

---

## 処理フローと問題発生箇所

### 処理フロー（概要）

```
Phase A: Preparation  → source ファイルの分類・catalog.json の生成
Phase B: Generation   → AI（Claude）が source から knowledge JSON を生成・キャッシュに保存
Phase C: Structure Check → knowledge JSON の構造バリデーション（S3/S4: index ↔ sections の整合性）
Phase D: Content Check → knowledge JSON のコンテンツ品質チェック
Phase E: Fix          → Phase D の指摘を AI が修正
Phase G: Resolve Links → RST ラベルを knowledge のセクション ID に解決
Phase M: Finalization → knowledge を plugin/knowledge/ にコピー・catalog 完成
```

### 問題の発生箇所

問題は **Phase B** で埋め込まれた。Phase B では AI（Claude）が source ドキュメントを読み、knowledge JSON を生成する。AI は以下の 2 点を誤ることがあった：

1. セクション ID を独自に命名する（スクリプト採番と乖離）
2. `processing_patterns` をデータフィールドでなく通常セクションとして出力する

これらは **AI の確率的な出力による誤り**であり、スクリプトの制御フローのバグではない。
一律ではなく一部のファイルにのみ発生しているのはこのためである。

## 発生事象と問題

### Phase C バリデーション失敗

`kc fix` 実行後（20260309T232615）、421件中418件が Phase C を通過し、3件が S3/S4 エラーで失敗していた。

| ファイルID | エラー |
|-----------|--------|
| `libraries-data_bind--sec-cd48d52b` | S4: sections key `section-extension` has no corresponding index entry |
| `libraries-data_bind--csv` | S3: index[].id `extension` has no corresponding section |
| `handlers-jaxrs_access_log_handler--sec-2a8f8aeb` | S4: sections key `processing-patterns` has no corresponding index entry |

Phase C の S3/S4 チェックは `phase_c_structure_check.py` で定義されており、knowledge ファイルの `index[].id` の集合と `sections` キーの集合が一致することを要求する。

### 根本原因：AI にセクション ID を命名させていた

Phase B のスクリプト（`phase_b_generate.py`）は RST セクションタイトルから `_title_to_section_id()` で ID を**スクリプト側で確定**できる。しかし当初のプロンプトは **タイトル名のみ** を AI に渡していた（ID を伝えていなかった）。

この設計により AI はセクション ID を独自に命名していた。スクリプトが採番した ID と AI が命名した ID が一致しないと、Phase C の S3/S4 エラーが発生する。また、RST の `.. _label:` ディレクティブから生成されるページ内・ページ間リンクは **スクリプト採番の ID** を前提として解決される（Phase G）。AI が異なる ID を付けた時点で、これらの ref 参照は消失・リンク切れとなっていた。

つまり、セクション ID の命名権は最初からスクリプトが持つべきだったが、AI に任せていたことが根本原因である。

### 根本原因：`processing_patterns` を AI に生成させていた

`processing_patterns` フィールドはソースドキュメントのコンテンツから導出するものではなく、**catalog.json の `type`/`category`** から機械的に決まる値である（`type == "processing-pattern"` なら `[category]`、それ以外は `[]`）。Phase M がこの値を読み取り、Phase F（`_file-search.md`）の絞り込みに使用する。

しかし Phase B では AI に `processing_patterns` の生成を任せており（プロンプトにフィールド定義があった）、AI は値を設定しないか、誤ってセクション（`sections["processing-patterns"]`）として出力することがあった。catalog から機械的に注入する後処理がなかったため、3 件のファイルに S4 エラーが発生し、421 件全件で `processing_patterns` フィールドが未設定となっていた。

### 2つの問題は独立している

| 問題 | 根本原因 |
|------|---------|
| S3/S4 エラー（セクションID不一致） | AI にセクション ID を命名させていた |
| `processing_patterns` 未設定 | catalog の値を AI 生成後に注入する後処理がなかった |

---

## 現状実装と対応方針

### 現状実装（対応前）

- `phase_b_generate.py` の `_build_prompt`: `{EXPECTED_SECTIONS}` にセクションのタイトルのみを渡していた（例: `- セクションタイトル`）
- Phase B: AI 生成後に `processing_patterns` を扱う後処理がなかった
- traceファイル（`{trace_dir}/{file_id}.json`）: `sections` リストのみ保存、RST ラベルとセクションIDの対応表は未保存
- `phase_g_resolve_links.py`: RST ラベルをセクションIDに変換する際、`_find_section_for_label` のヒューリスティック推定のみ使用
- 既存 421 件のキャッシュファイル: `processing_patterns` フィールドなし

### 対応方針

症状修正（キャッシュファイルの手動直し）ではなく、スクリプトによる採番結果を AI に伝え、AI 生成後にスクリプトが正しい値を上書きする仕組みを実装する。既存キャッシュはマイグレーションで修正する。

---

## 具体的な対応内容

### 1. Phase B: プロンプトへのセクションID付与（`phase_b_generate.py`）

`_build_prompt` 内の `{EXPECTED_SECTIONS}` 組み立て処理を変更し、各セクションにスクリプト採番の ID を明示する。

**変更前**:
```
- セクションタイトル
```

**変更後**:
```
- セクションタイトル (ID: section-id)
```

`section_id` は `_title_to_section_id(title)` で算出する。この関数は `step2_classify.py` に定義されており、ASCII英数字部分をkebab-caseに変換し、日本語タイトル等は `sec-{md5前8桁}` にフォールバックする。

プロンプト（`generate.md`）にも「括弧内の ID を必ずそのまま使用すること」という指示を追加した。

### 2. Phase B: `_post_process_knowledge` による後処理追加（`phase_b_generate.py`）

AI 生成後の knowledge オブジェクトに対して `_post_process_knowledge` を適用する。処理内容：

- `sections["processing-patterns"]` が存在する場合、取り出して削除する
- `index` から `id == "processing-patterns"` のエントリを削除する
- top-level `processing_patterns` を以下のルールで設定する：
  - `file_info["type"] == "processing-pattern"` の場合: `[file_info["category"]]`
  - `processing_patterns` が未設定で sections に値があった場合: その値をリスト化
  - それ以外: `[]`（空配列）

### 3. Phase B: `label_to_section_id` を trace に保存（`phase_b_generate.py`）

traceファイルに RST ラベルとセクションIDの対応表 `label_to_section_id` を追加保存する。

構築方法：RST ソースから `_extract_rst_labels` で抽出したラベルを走査し、trace の `sections` リスト内の `section_id` とマッチするものを対応付ける。マッチ条件はラベルとセクションIDの完全一致、またはハイフン/アンダースコア正規化後の一致。

### 4. Phase G: trace の `label_to_section_id` を優先使用（`phase_g_resolve_links.py`）

`_build_label_index` 内で trace を読み込む際、`label_to_section_id` が存在する場合はそのマッピングを `self.label_index` に直接登録する。従来のヒューリスティック推定（`_find_section_for_label`）はフォールバックとして維持する。

### 5. マイグレーション（`migrate_add_processing_patterns.py`）

既存 421 件のキャッシュファイルに対し、以下を実行する：

- **3件の S3/S4 エラーファイル**に個別修正を適用：
  - `libraries-data_bind--sec-cd48d52b`: `sections["section-extension"]` を `sections["extension"]` にリネームし、`index` に `extension` エントリを追加
  - `libraries-data_bind--csv`: `index` から孤立した `extension` エントリを削除
  - `handlers-jaxrs_access_log_handler--sec-2a8f8aeb`: `sections["processing-patterns"]` を取り出し、top-level `processing_patterns` に設定
- **全 421 件**に `processing_patterns` フィールドが存在しない場合は `[]` を追加

---

## 対応内容でなぜ解決するのか？

### S3/S4 エラーの解決

**プロンプトへのID明示（対応1）**: 以降の新規生成において、AI がスクリプトの採番と異なるセクションIDを使用する原因は「AI がタイトルから独自にIDを命名していた」点にある。タイトルと共にスクリプト採番の ID を渡し、かつ「そのまま使うこと」と指示することで、AI はスクリプト採番のIDを採用する。

**後処理による強制修正（対応2）**: AI が `processing-patterns` をセクションとして出力した場合でも、`_post_process_knowledge` がそれを検出して `sections` と `index` から除去し、top-level `processing_patterns` に移動する。この処理はスクリプト側で完結するため、AI の出力に依存しない。

**マイグレーション（対応5）**: 既存の 3 件の S3/S4 エラーファイルに対して、個別の修正関数を適用する。各修正内容は Phase C の検証ルール（S3: index エントリに対応する section が必要、S4: section キーに対応する index エントリが必要）を満たすように設計されている。

### `processing_patterns` 欠落の解決

**後処理（対応2）** により、Phase B で生成するすべての新規ファイルに `processing_patterns` が設定される。**マイグレーション（対応5）** により、既存 421 件に `[]` 以上の値が設定される。

### Phase G のリンク解決改善（対応3・4）

Phase G は RST の `.. _label:` ディレクティブから生成したリンクを、knowledge ファイルのセクションIDに解決する。従来のヒューリスティックが失敗していたケースに対し、Phase B が実際に使用したセクションIDの対応表を trace に保存し、Phase G がそれを参照することで確定的に解決できる。

---

## 対応内容で新たな問題が発生しない根拠は？

### `_post_process_knowledge` のロジック

- `sections["processing-patterns"]` の除去は、該当キーが存在する場合のみ動作する（`dict.pop` のデフォルト引数に `None`）。存在しない場合は何もしない。
- `index` からの `processing-patterns` エントリ除去はリスト内包表記によるフィルタリングで、存在しない場合も安全に動作する。
- top-level `processing_patterns` の設定は「未設定の場合のみ」を条件としており（`"processing_patterns" not in knowledge`）、AI が正しく設定した場合はその値を保持する。
- `file_info["type"] == "processing-pattern"` の場合のみ catalog の category を使用し、それ以外の processing-pattern type は空配列をデフォルトとする。これは catalog.json の `processing_patterns` データ（全 421 件のうち 82 件が非空、339 件が空）と整合している。

### Phase G のフォールバック維持

trace に `label_to_section_id` が存在しない場合（古い trace ファイル、または RST 以外のフォーマット）は、従来のヒューリスティック（`_find_section_for_label`）にフォールバックする。新旧 trace ファイルのどちらでも動作する。

### マイグレーションスクリプトの安全性

- 各ファイルの修正は独立した関数で実装され、対象ファイルIDが完全一致する場合のみ適用される。
- `--dry-run` オプションで実際の書き込みなしに確認できる設計になっている（スクリプトに引数定義あり）。
- `processing_patterns` の追加は `"processing_patterns" not in knowledge` を条件とし、既存値があれば上書きしない。

### テスト

- `tests/ut/test_phase_b_processing_patterns.py`（新規）: `_post_process_knowledge` の主要ケース（sections からの移動、type=processing-pattern 時の注入、フィールド未存在時の空配列追加、index エントリの除去）を網羅
- `tests/ut/test_phase_g.py`（追加）: `label_to_section_id` を持つ trace を使用した場合のリンク解決動作を検証
- 全テスト実行結果: 136 passed, 7 skipped

---

## ユーザー観点での後方互換への影響は？

**影響なし。**

今回の変更は knowledge-creator（`kc` コマンド）の内部処理と、knowledge ファイルの内容品質に関するものである。ユーザーが操作するインターフェース（`/n6` コマンド、nabledge プラグインの API）に変更はない。

knowledge ファイルの `processing_patterns` フィールドに値が設定されることで、処理方式別の絞り込み検索が意図通りに機能するようになる。これはユーザーにとって検索精度の向上であり、退行ではない。

---

## kcと生成済みファイル（キャッシュ含む）観点での後方互換への影響は？

### kc コマンドの挙動変化

| 操作 | 変化 |
|------|------|
| `kc gen`（新規生成） | `_post_process_knowledge` が適用されるため、生成ファイルに `processing_patterns` が必ず含まれる。プロンプトのセクションID指示が変わるため、以前と全く同一の出力にはならない可能性がある（AI の確率的出力による） |
| `kc gen --resume` | キャッシュ済みファイルはスキップされるため、影響なし |
| `kc regen --target <id>` | 指定ファイルは再生成されるため、上記「新規生成」と同じ |
| `kc fix` | Phase E の修正フローは変更なし |
| Phase C チェック | バリデーションルール自体の変更なし。正しく生成されたファイルは引き続き pass する |
| Phase G | `label_to_section_id` が trace にある場合はそれを使用。ない場合はフォールバック。既存 trace との後方互換あり |

### 既存キャッシュファイルへの変更

マイグレーションスクリプト（`migrate_add_processing_patterns.py`）を実行済みであり、以下の変更がコミット済み：

- 421 件全ファイル: `processing_patterns` フィールドを追加（既存値があれば維持）
- `libraries-data_bind--sec-cd48d52b`: `sections["section-extension"]` → `sections["extension"]` にリネーム、index に `extension` エントリ追加
- `libraries-data_bind--csv`: index から孤立した `extension` エントリを削除
- `handlers-jaxrs_access_log_handler--sec-2a8f8aeb`: `sections["processing-patterns"]` を除去し top-level `processing_patterns` に移動

これらの変更後、Phase C: 421/421 pass が確認済み。

### catalog.json への変更

421 件のファイルエントリすべてに `processing_patterns` フィールドが追加された（従来は一部のエントリにのみ存在）。kc の Phase A/B がこのフィールドを参照する際に参照可能になる。
