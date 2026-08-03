Rn version: 0.8.0

# Goal

README に開発ワークフロー全体（スキル改善・バグ修正・Nablarch ソース更新・ベンチマーク実行・リリース前セットアップ検証）を追加し、開発者がどの作業を始める場合でもリポジトリ外を探さずに開始できるようにする。

# Acceptance criteria

- [ ] README の「開発」セクションに「スキルの改善・バグ修正」エントリがあり、`/hi` コマンドの使い方・RBKC による知識ファイル再生成手順（`bash tools/rbkc/rbkc.sh create <v>` / `verify <v>`）・5バージョン全件適用ルールへの参照が記載されている
- [ ] README の「開発」セクションに「Nablarch ソース更新」エントリがあり、`./setup.sh` で `.lw/nab-official/` が更新される旨と、更新後に RBKC を再実行して知識ファイルを再生成する流れが記載されている
- [ ] README の「開発」セクションに「ベンチマーク」エントリがあり、`tools/benchmark/HOW-TO-RUN.md` を参照する導線（何の数字を測り、どこを読めばよいか）が記載されている
- [ ] README の「リリース手順」セクションに「リリース前セットアップ検証」エントリがあり、`bash tools/tests/test-setup.sh` の実行方法と合否判定の参照先（`tools/tests/README.md`）が記載されている
- [ ] 既存の README 内容（セットアップ・ブランチ戦略・カスタムコマンド・フィードバック）が変更・欠落していない
- [ ] 追加した内容に誤りがなく、実際のツールの動作・コマンドと一致している

# Assumptions

- `./setup.sh` を再実行すると `.lw/nab-official/` の git リポジトリ群が `git pull` で更新される（`clone_or_update_repo` の挙動から確認済み）
- SVN ベースの v1.x は `svn update` で更新される（`setup.sh` の `svn_checkout` 関数から確認済み）
- README の主な読者は日本語話者（既存 README が日本語）
- ベンチマークの詳細手順は `tools/benchmark/HOW-TO-RUN.md` に完備されているため、README は導線のみ

# Rules

- commit and push every change; one completion marker per task
- README は日本語で記述する（既存 README の言語ポリシーに合わせる）
- 既存の README 見出し・文体・フォーマットを踏襲する
- 追加コンテンツは既存ツールドキュメントと矛盾しないこと

# Tasks

### #1: README に開発ワークフローセクションを追加する

**Purpose**: README の「開発」セクションに、スキル改善・バグ修正・Nablarch ソース更新・ベンチマークの 3 トピックを追加する

**Prerequisites**: none

**Steps**:

- [ ] 既存 README の「開発」セクションの構成を確認し、追加する場所を決める
- [ ] 「スキルの改善・バグ修正」サブセクションを追加する（`/hi` 使い方、RBKC 再生成、5バージョンルール参照）
- [ ] 「Nablarch ソース更新」サブセクションを追加する（`./setup.sh` で更新、RBKC 再実行）
- [ ] 「ベンチマーク」サブセクションを追加する（目的の説明、`HOW-TO-RUN.md` への参照）
- [ ] self-check (OK/NG per completion criterion, record in checks/01.md)
- [ ] QA expert review (subagent)
- [ ] Technical Writer expert review (subagent)

**Completion criteria**:

- `README.md` の「開発」セクション内に「スキルの改善・バグ修正」「Nablarch ソース更新」「ベンチマーク」の 3 エントリが存在し、それぞれのコマンド・参照先が正確に記載されている（実際のツールコマンドと一致すること）
- 既存の README コンテンツ（セットアップ・ブランチ戦略・カスタムコマンド・フィードバックセクション）が変更・欠落していない

### #2: README にリリース前セットアップ検証を追加する

**Purpose**: README の「リリース手順」セクションに、リリース前の `test-setup.sh` 実行手順を追加する

**Prerequisites**: #1

**Steps**:

- [ ] 既存 README の「リリース手順」セクションの構成を確認し、追加する場所を決める
- [ ] 「リリース前セットアップ検証」エントリを追加する（`bash tools/tests/test-setup.sh` の実行・参照先）
- [ ] self-check (OK/NG per completion criterion, record in checks/02.md)
- [ ] QA expert review (subagent)
- [ ] Technical Writer expert review (subagent)

**Completion criteria**:

- `README.md` の「リリース手順」または隣接するセクションに「リリース前セットアップ検証」エントリが存在し、`bash tools/tests/test-setup.sh` のコマンドと `tools/tests/README.md` への参照が記載されている
- 既存の「リリース手順」セクションの内容が変更・欠落していない

### #3: Evaluation sign-off

**Purpose**: 受け入れ基準の全項目が満たされていることをユーザーが確認し、セッションを承認する

**Prerequisites**: #1, #2

**Steps**:

- [ ] Acceptance criteria の全項目を実行確認し結果を提示する
- [ ] ユーザーから `/rn:ty` (承認) または `/rn:gm` (修正依頼) を受け取る

**Completion criteria**:

- Acceptance criteria の全 6 項目が満たされていることがユーザーにより確認され、`/rn:ty` で承認されている

# State

<!-- rn managed — do not edit -->

