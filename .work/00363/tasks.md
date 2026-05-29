# Tasks: Add Javadoc knowledge to nabledge skills

**PR**: (TBD)
**Issue**: #363
**Updated**: 2026-05-29

## Rules (applied to every task)

- 1コミット = 1タスク（粒度を守る）
- SCを満たすようタスクを分割し、このファイルで管理する
- 推測せず事実ベースで調査・作業・判断する（実物・全件を確認し、確認範囲を明示する）
- 既存の RST/MD/xlsx パイプラインには一切触れない（追加のみ）
- RBKCのcreate/verifyを変更する場合は実装前に設計書を更新してユーザーに確認する
- PRレビュー依頼前に、変更差分が想定どおりの変更のみかをチェックし、結果を作業記録に出力してユーザーに確認する
- 全タスク共通: 変更差分チェック → ユーザー確認 → PRレビュー依頼の順を守る

---

## Not Started

### Task 0: Investigate jar tool input/output format
**Goal**: SC「Investigate: Identify the input/output format of the provided jar tool (source file → Markdown)」を満たす。  
**Steps:**
- [ ] ユーザーに jar ファイルの入手方法・場所を確認する（jarはissue説明によると「実装時に提供」とある）
- [ ] jar を実際に動かしてサンプル出力（Markdown）を取得する
- [ ] 出力 Markdown の構造を全件確認する（クラス1つ分・パッケージ複数分）
- [ ] 入力形式（ソースファイルのパス指定方法・オプション）を確認する
- [ ] 調査結果を `.work/00363/notes.md` に記録する

### Task 1: Investigate RBKC integration point (all 5 versions)
**Goal**: SC「Investigate: Determine appropriate integration point in the RBKC pipeline across all 5 versions」を満たす。  
**Steps:**
- [ ] 各バージョン（v6/v5/v1.4/v1.3/v1.2）のNablarchソースJarの取得方法を調査する（Mavenリポジトリ等）
- [ ] `.lw/nab-official/` 配下の各バージョンのディレクトリ構成を全件確認する
- [ ] 各バージョンで「どのNablarchクラスのJavadocが必要か」を調査する（RST中の `:javadoc_url:` 参照38箇所を全件確認）
- [ ] 新フォーマット（`javadoc`）を既存パイプラインに追加する場合の影響範囲を調査する
  - `scan_sources()` への追加箇所
  - `_converter_for()` への追加箇所
  - `mappings/v*.json` への追加箇所
  - `verify.py` への影響（既存チェックの非適用対象にするか否か）
- [ ] 既存テスト（e2e/ut）への影響を全件確認する
- [ ] 調査結果を `.work/00363/notes.md` に記録する

### Task 2: Design — Javadoc converter and pipeline integration
**Goal**: 実装前設計書の作成とユーザー承認。  
**前提**: Task 0, Task 1 完了後  
**Steps:**
- [ ] jar 出力 Markdown → knowledge JSON への変換仕様を設計する
- [ ] verify が Javadoc 知識ファイルをどう扱うか設計する（既存チェック全適用 / 一部除外 / 専用チェック追加）
- [ ] 全5バージョンへの適用方針を設計する（バージョン固有の差異があれば記録）
- [ ] 設計書を `tools/rbkc/docs/` に追加する
- [ ] 設計書をコミットし、PRコメントでユーザーに確認を依頼する
- [ ] ユーザー承認後に実装フェーズへ進む

### Task 3: Implement — jar runner script (Javadoc Markdown generation)
**Goal**: 全5バージョンの全 public Nablarchクラスの Javadoc Markdown を生成する。  
**前提**: Task 2 完了後  
**Steps:**
- [ ] jar を実行して Javadoc Markdown を生成するスクリプトを作成する（`tools/rbkc/scripts/` 配下）
- [ ] 全5バージョンで動作確認する
- [ ] 生成ファイル数・内容を全件確認し、結果を作業記録に記録する

### Task 4: Implement — Javadoc converter (`converters/javadoc.py`)
**Goal**: jar 出力 Markdown → knowledge JSON への変換器を実装する。  
**前提**: Task 2, Task 3 完了後  
**Steps:**
- [ ] `tools/rbkc/scripts/create/converters/javadoc.py` を新規作成する（既存ファイルに一切触れない）
- [ ] TDD: テストを先に書く（RED）
- [ ] 実装（GREEN）
- [ ] 全既存テストが通ることを確認する: `pytest tools/rbkc/tests/ -x`

### Task 5: Implement — Pipeline integration (scan/classify/run)
**Goal**: 新フォーマット `javadoc` を RBKC パイプラインに追加する。  
**前提**: Task 4 完了後  
**Steps:**
- [ ] `mappings/v*.json` に Javadoc エントリを追加する（全5バージョン）
- [ ] `scan_sources()` に `.md`（Javadoc生成済みMD）のスキャン対応を追加する（既存MDスキャンと衝突しない形で）
- [ ] `_converter_for()` に `javadoc` フォーマットの dispatch を追加する
- [ ] `rbkc.sh create <v>` を全5バージョンで実行し、Javadoc 知識ファイルが生成されることを確認する
- [ ] 全既存テストが通ることを確認する: `pytest tools/rbkc/tests/ -x`

### Task 6: Implement — verify compatibility (all 5 versions)
**Goal**: `rbkc.sh verify <v>` が全5バージョンで FAIL 増加なしで通ること。  
**前提**: Task 5 完了後  
**Steps:**
- [ ] 各バージョンの create 前後の FAIL 数をベースラインとして記録する
- [ ] `rbkc.sh create <v> && rbkc.sh verify <v>` を全5バージョンで実行する
- [ ] FAIL 差分を分析する（想定外の増加があれば RBKC 側を修正する）
- [ ] verify に Javadoc 専用チェックが必要な場合は設計書を更新してユーザー確認を得る
- [ ] 全バージョンで FAIL 増加なしを確認する

### Task 7: Benchmark — verify scores do not decrease (all 5 versions)
**Goal**: SC「Benchmark scores for all 5 versions do not decrease vs. baseline after adding Javadoc knowledge」を満たす。  
**前提**: Task 6 完了後  
**Steps:**
- [ ] nabledge-test ベースラインスコアを確認する（MEMORY.md 記載の最新ベースライン）
- [ ] 各バージョンでベンチマークを実行する（逐次実行 — 並列不可、tools/benchmark/run.py を使用）
- [ ] スコア比較結果を `.work/00363/notes.md` に記録する
- [ ] スコア低下があれば原因を特定して修正する

### Task 8: Diff check and PR review request
**Goal**: 全タスク完了後、変更差分が想定どおりかをチェックしてPRを作成する。  
**前提**: Task 7 完了後  
**Steps:**
- [ ] `git diff main...HEAD --stat` で変更ファイル一覧を確認する
- [ ] 想定外の変更がないかを全件チェックし、`.work/00363/diff-check.md` に記録する
- [ ] ユーザーに確認を依頼する
- [ ] Expert review を実行する（Software Engineer + QA Engineer）
- [ ] `/pr create` でPRを作成する

---

## Done

（なし）
