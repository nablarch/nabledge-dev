# Nabledge設計書

**作成日**: 2026年2月10日
**バージョン**: 1.4
**ステータス**: Draft

## 変更履歴

| バージョン | 日付 | 変更内容 |
|----------|------|---------|
| 1.4 | 2026/02/10 | 代行業務の整理、文体統一 |
| 1.3 | 2026/02/10 | アーキテクチャレビュー反映 |
| 1.2 | 2026/02/10 | MCP削除、簡潔化 |
| 1.0 | 2026/02/09 | 初版作成 |

---

## 1. 概要

### 1.1 背景と目的

**Nabledgeとは**:
Nablarchの構造化知識と、それを活用して開発作業を代行するワークフローで構成される、AIエージェント（Claude Code、GitHub Copilot）向けの知識基盤です。

**解決する課題**: AI単体ではNablarch固有の知識がなく代行精度が不十分なこと、公式ドキュメントは人間向けでAIが効率的に検索・参照できないこと、新規参画者のオンボーディングや日常開発に時間がかかることです。

**目的**: AIエージェントにNablarchの構造化知識を提供し、実装調査・コード生成・レビュー等の代行精度向上、開発工数の削減（目標: 60-70%）、オンボーディング期間の短縮を実現します。

---

### 1.2 想定する代行作業

| 代行業務 | 優先度 | 優先度理由 | Nabledge代行適性 |
|---------|:------:|-----------|:---------------:|
| 既存コード理解 | S | 知識基盤の構築に必須 | 高 |
| ナレッジQ&A | S | 知識基盤の構築に必須 | 高 |
| 影響分析 | A | プロジェクトでの要望が多い | 中 |
| レビュー | A | プロジェクトでの要望が多い | 高 |
| コード生成・雛形作成 | B | | 中 |
| 実装調査 | B | | 中 |
| テストデータ作成 | B | | 低 |
| 障害調査 | B | | 中 |
| 設計書解読 | B | | 低 |
| ドキュメント生成 | B | | 低 |

**Nabledge代行適性**:
- **高**: Nablarch知識だけで対応可能
- **中**: Nablarch知識に加えてPJ固有知識が必要
- **低**: PJ固有知識が多く必要

---

### 1.3 スコープ

**対象**: Nablarchバッチ（都度起動型）、RESTful Webサービス

**対象外**: Jakarta Batch、常駐バッチ、ウェブアプリケーション（JSP/画面）、メッセージング（MOM）

**対象バージョン**: Nablarch 6系、5系、1.4系、1.3系、1.2系

**想定ツール**: Claude CodeとGitHub Copilotの両方に対応します。

---

## 2. アーキテクチャ

### 2.1 全体構造

```mermaid
graph TB
    %% 左側: 主要アクター
    subgraph main_actors["🎭 主要アクター"]
        direction TB
        DEV["👥 Nablarch利用者<br/>(アプリケーション開発者)"]
        AGENT["🛠️ AIツール<br/>(Claude Code/GitHub Copilot等)"]
        DEV -->|"①自然言語で依頼<br/>(例: ページングを実装したい)"| AGENT
    end

    %% 中央: nabledgeスキル
    subgraph nabledge["📦 nabledgeスキル"]
        direction TB

        subgraph workflows["🤖 ワークフロー（LLM実行）"]
            WF_SEARCH["知識検索<br/>(keyword+intent並列)<br/>関連度判定"]
            WF_DELEGATE["代行作業<br/>実装調査・コード生成・レビュー"]
            WF_GENERATE["知識ファイル生成・検証<br/>3分/ファイル・20%サンプリング"]
        end

        subgraph knowledge["知識基盤"]
            INDEX["インデックス(TOON)<br/>93エントリ・650検索ヒント"]
            JSON["知識ファイル(JSON)<br/>60ファイル・420Kトークン"]
            MD["知識ファイル(Markdown)<br/>人間確認用・根拠追跡"]
        end
    end

    %% 右側: Nablarch開発チーム
    subgraph dev_team["👨‍💻 Nablarch開発チーム"]
        NAB_TEAM["Nablarch開発チーム<br/><br/>• 公式情報更新<br/>• 知識レビュー・承認"]
    end

    %% 主要フロー（①→⑤）
    AGENT -->|"②知識検索"| WF_SEARCH
    WF_SEARCH -->|"検索"| INDEX
    INDEX -->|"③関連セクション特定<br/>(関連度: High/Partial)"| JSON
    JSON -.->|"自動変換"| MD

    AGENT -->|"④ワークフロー実行"| WF_DELEGATE
    WF_DELEGATE -->|"知識参照<br/>(上位10セクション)"| JSON
    WF_DELEGATE -->|"⑤回答・コード生成"| DEV

    %% 開発チームフロー
    AGENT -.->|"実行"| WF_GENERATE
    WF_GENERATE -.->|"作成・検証"| JSON
    NAB_TEAM -.->|"更新時"| WF_GENERATE
    NAB_TEAM -.->|"レビュー・承認"| JSON

    MD -.->|"人間が確認"| DEV

    %% 下部: GitHub配布
    subgraph github["📦 GitHub"]
        direction TB
        subgraph org["org: nablarch"]
            REPO["repository: nabledge<br/><br/>• Claude Code Pluginとして配布<br/>• claude plugin install nabledge-6<br/>• バージョン管理"]
        end
    end

    %% 配布フロー
    nabledge -.->|"取得"| REPO

    %% スタイル
    style main_actors fill:#e1f5ff
    style dev_team fill:#ffe1f5
    style nabledge fill:#f0f0f0
    style github fill:#f5f5f5
    style org fill:#e8f5e9
    style knowledge fill:#e8f5e9
    style workflows fill:#fff9c4
```

**実行フロー**:
1. Nablarch利用者が自然言語でAIツールに依頼します（例: 「ページングを実装したい」）
2. AIツールがワークフロー（知識検索）を実行します → keyword + intent並列検索
3. 関連度の高いセクションを特定します（High/Partial/Noneの3段階）
4. ワークフロー（代行作業）を実行し、知識ファイルを参照します（上位10セクション ≈ 5,000トークン）
5. 回答またはコードを生成してユーザーに返します

**設計のポイント**:
- **配布**: GitHub (nablarch/nabledge) → Claude Code Plugin → インストール
- **検索**: keyword（技術軸）+ intent（目的軸）の並列実行で漏れを防止します
- **トークン効率**: TOON形式で30-60%削減、セクション単位抽出で必要最小限に抑えます
- **正確性**: 公式ドキュメント照合、人向けMarkdownで根拠追跡します
- **保守性**: JSON→MD自動変換で1箇所メンテナンス、バージョン別スキル分離します

---

### 2.2 知識タイプ

| # | 知識タイプ | 内容 | カバー範囲 | 作成単位 | 推定件数 |
|---|-----------|------|----------|---------|---------|
| ① | 機能・実装パターン（エラー含む） | どう実装するか、エラー対処 | 9タスク（90%） | ハンドラ、ライブラリ、処理方式、ツール、アダプタ | 約55個 |
| ② | チェック項目 | 何に気をつけるべきか | 3タスク（30%） | セキュリティ、推奨/非推奨、公開API | 3個 |
| ③ | リリースノート | 何が変わった/壊れているか | 2タスク（20%） | バージョン単位 | 複数個 |
| **合計** | | | | | **約60個** |

**設計判断**: ①を優先的に構造化すれば9割の作業をカバー可能です。①から着手します。

---

### 2.3 配布とインストール

#### 配布形式

[Claude Code Plugin](https://code.claude.com/docs/en/plugins)として配布します。

**配布元**: GitHub (`github.com/nablarch/nabledge`)

**配布フロー**:
```
GitHub (nablarch/nabledge)
  ↓ Claude Code Plugin Registry
  ↓ claude plugin install nabledge-6
ユーザー環境 (.claude/skills/nabledge-6/)
```

#### インストール方法

**Claude Code**:
```bash
# Plugin Registryからインストール
claude plugin install nabledge-6

# 確認
claude plugin list

# アップデート
claude plugin update nabledge-6
```

**GitHub Copilot**:
プロジェクトルートに`.claude/skills/nabledge-6/`を配置し、設定ファイルに登録します。

**設計判断**: Claude Codeの標準配布方式を採用します。GitHubからの自動取得、バージョン管理、更新通知が容易です。

---

### 2.4 ファイル構成

```
nabledge-6/
├── SKILL.md                    # スキル定義
├── knowledge/                  # 知識
│   ├── index.toon              # 検索インデックス（TOON形式）
│   ├── features/               # ① 機能・実装パターン
│   │   ├── handlers/           # ハンドラ単位
│   │   ├── libraries/          # ライブラリ単位
│   │   ├── processing/         # 処理方式単位
│   │   ├── tools/              # ツール単位
│   │   └── adapters/           # アダプタ単位
│   ├── checks/                 # ② チェック項目
│   └── releases/               # ③ リリースノート
├── workflows/                  # ワークフロー（代行単位）
├── scripts/                    # スクリプト
├── assets/                     # アセット
└── docs/                       # 人向け閲覧用（JSON→MD自動変換）
```

**命名規則**: 英語、kebab-case（例: `db-connection-management-handler.json`）

**設計判断**: バージョン情報はファイル名に含めません（スキル自体がバージョン別のため冗長です）。

---

### 2.5 検索アーキテクチャ

#### 2つの検索方式

| 検索名 | 切り口 | 説明 |
|--------|--------|------|
| keyword-search | 技術軸 | index.toonのhintsでキーワードマッチ |
| intent-search | 目的軸 | 目的→カテゴリ、対象→ファイルで絞込 |

**設計判断**: 単一検索では漏れが発生しやすいため、異なる切り口で並列実行し、結果をマージすることで漏れを防止します。

#### 検索結果構造（pointers）

```json
{
  "files": [
    { "id": "F1", "path": "features/libraries/universal-dao.json", "relevance": 2 }
  ],
  "sections": [
    { "file_id": "F1", "section": "paging", "relevance": 2, "matched_hints": ["ページング", "per", "page"] }
  ]
}
```

**設計判断**:
- sections を関連度降順でソートすることで、最重要セクションから読めます
- files でファイル単位の重要度を把握できます
- ファイルパスは1回だけ出現し、file_idで参照します（重複排除）

#### 関連度定義

| レベル | 値 | 判断基準 |
|:------:|:---:|---------|
| **High** | 2 | 依頼に直接回答できる |
| **Partial** | 1 | 依頼に関連し、補足として有用 |
| **None** | 0 | 関連なし（対象外） |

**ファイルの関連度**: そのファイル内のセクション関連度の最大値

**設計判断**: 情報検索分野の標準的なgraded relevanceを採用します。3段階で十分な精度が得られます。

---

### 2.6 インデックス設計（index.toon）

#### TOON形式

```toon
# Nabledge-6 Knowledge Index

files[N,]{path,hints}:
  features/handlers/common/global-error-handler.json, グローバルエラーハンドラ GlobalErrorHandler 未捕捉例外 エラーハンドリング 例外処理
  features/libraries/universal-dao.json, ユニバーサルDAO UniversalDao CRUD 検索 ページング
```

**構造**:
- `files[N,]{path,hints}:` → N件の配列、フィールドはpath, hints
- 各行: `パス, スペース区切りの検索ヒント`

**規模**: 93エントリ、約650検索ヒント → 約5-7Kトークン

**設計判断**: TOON形式はJSONより30-60%トークン削減します。LLMフレンドリーで高効率です。

#### 検索ヒント設計指針

**3段階のキーワード抽出**:

知識ファイルの検索ヒントは、以下の3段階でキーワードを抽出します。このうち2段階以上でマッチすることを推奨します。

1. **Technical domain（技術領域）**: データベース, バッチ, ハンドラ, Web, REST, テスト など
2. **Technical component（技術要素）**: DAO, JDBC, JPA, Bean Validation, JSON, XML など
3. **Functional（機能）**: ページング, 検索, 登録, 更新, 削除, 接続, コミット など

**例**: 依頼「ページングを実装したい」の場合
- Technical domain: ["データベース", "database"]
- Technical component: ["DAO", "UniversalDao", "O/Rマッパー"]
- Functional: ["ページング", "paging", "per", "page", "limit", "offset"]

**基本指針**:

| 項目 | 指針 |
|------|------|
| 言語 | 日本語基本。公式で英語のものはそのまま |
| 語数 | ファイル: 5-10語、セクション: 3-5語 |
| 順序 | 広い技術領域→詳細（降順）例: `DB 接続 コネクション` |
| 表記揺れ | 複数表記を含める（例: DB, データベース, database） |

**設計判断**: 3段階でキーワードを網羅的に抽出し、2段階以上でマッチさせることで検索精度を向上させます。

---

### 2.7 知識ファイル設計（JSONスキーマ）

#### 共通構造

```json
{
  "schema_version": "1.0",
  "id": "ファイル識別子",
  "title": "タイトル（日本語）",
  "official_doc_urls": ["https://nablarch.github.io/docs/..."],
  "index": [
    { "id": "セクションID", "hints": ["検索ヒント1", "検索ヒント2"] }
  ],
  "sections": {
    "overview": {
      "summary": "100-200文字の要約",
      /* セクション固有のプロパティ */
    },
    "セクションID": { /* ... */ }
  }
}
```

**設計判断**:
- **JSON形式**: パース容易、jqでセクション抽出可能、構造化データとして扱いやすいです
- **二層構造（JSON + Markdown）**: AI向けJSON、人向けMD（自動変換）でメンテナンス1箇所で済みます
- **スキーマバージョニング**: 非互換変更時にメジャーバージョンアップします（1.0 → 2.0）

#### 情報の持ち方の原則

| 原則 | 説明 | 判断基準 |
|------|------|---------|
| **仕様は全部残す** | 必須/オプション、推奨/非推奨も網羅します | 設定項目、デフォルト値、型、制約、動作仕様、理由・背景、注意点、警告をすべて含みます |
| **考え方も全部残す** | 理由・背景・なぜそうするかを残します | 設計思想、推奨パターン、注意事項をすべて含みます |
| **表現は最適化する** | 読み物的記述→端的な記述にします | 導入文、冗長な説明、重複表現、段階的な説明を削除し、箇条書き化します |
| **形式はAI向けに** | 構造化データで検索・参照しやすくします | JSON形式、検索ヒント設計を採用します |

**設計判断**: 「この情報がないとAIが誤った判断をする可能性があるか？」で判断します。YESなら残し、NOなら最適化します。

---

### 2.8 コンテキスト管理

#### コンテキストウィンドウへの適合

**制約**:
- Claude Opus 4.6のコンテキストウィンドウ: 200,000トークン
- 全60ファイルの推定トークン数: 約420,000トークン

**対策**:
1. **セクション単位の抽出**: 関連度の高いセクションのみを抽出します
   - 上位10セクション（平均500トークン）= 約5,000トークン（全体の2.5%）
2. **関連度による絞り込み**: High（2点）のセクションを優先します
3. **動的調整**: コンテキスト使用率に応じて取得セクション数を調整します

**設計判断**: ファイル全体を取得するのではなく、セクション単位で抽出することで、コンテキストウィンドウ内で運用可能にします。

#### 上位N件抽出の根拠

| 項目 | 推奨値 | 根拠 |
|------|--------|------|
| files | 上位5件 | 1ファイル平均2000トークン × 5 = 10,000トークン |
| sections | 上位10件 | 1セクション平均500トークン × 10 = 5,000トークン |
| 合計 | 約15,000トークン | コンテキストの7.5%程度、他の情報と併用可能 |

**動的調整**:
- High（2点）のセクションが10件未満 → Partial（1点）も含めて最大15件まで拡張します
- High（2点）のセクションが20件以上 → 上位15件まで拡張します
- コンテキスト使用率が80%超 → セクション数を減らします（最小5件）

**設計判断**: 依頼の複雑さに応じて情報量を動的調整し、精度とトークン効率を両立します。

---

## 3. 実装計画

### 3.1 作成範囲

**情報源**:
- Nablarch公式解説書（https://nablarch.github.io/docs/LATEST/doc/）
- システム開発ガイド（https://fintan.jp/page/252/）- パターン集、アンチパターン
- サンプルプロジェクト（GitHub: nablarch/nablarch-example-batch, nablarch-example-rest）

**作成規模**: 約60個の知識ファイル

| 作成単位 | 推定件数 | 備考 |
|---------|---------|------|
| 処理方式 | 2個 | Nablarchバッチ、RESTful |
| ライブラリ | 約15個 | DB、ファイルI/O、バリデーション等 |
| ハンドラ | 約20個 | 共通、バッチ専用、REST専用 |
| ツール | 約5個 | NTF、gsp-dba-maven-plugin等 |
| アダプタ | 約13個 | ログ、DB、REST、メール等 |
| チェック項目 | 3個 | セキュリティ、推奨/非推奨、公開API |
| リリースノート | 複数個 | バージョン別 |

---

### 3.2 フェーズ計画

#### フェーズ1: Nabバッチ（FW）- バッチフレームワーク完成（優先度: 最高）

**期間**: 1週間
**作業量**: 約1.5時間（作成45分 + 品質チェック45分）
**対象**: バッチ専用ハンドラ約10個、バッチで使うライブラリ約5個
**目的**: なるべく早くAIのメリットを感じてもらうことです

**仮説検証**:
- 代行精度を実測します（実装調査、コード生成、レビュー等）
- 工数削減を実測します（従来工数 vs 代行後工数）
- 目標: 工数削減60%以上
- 効果確認後、フェーズ2以降へ進みます

#### フェーズ2: Nabバッチ（NTF）- テストフレームワーク完成

**期間**: 3日
**作業量**: 約30分
**対象**: NTF関連の残り約1-2個

#### フェーズ3: REST（API）- RESTful Webサービス対応

**期間**: 1週間
**作業量**: 約1時間
**対象**: RESTful処理方式1個、REST専用ハンドラ約5個、REST関連ライブラリ約3個

#### フェーズ4: 残り - 網羅性確保

**期間**: 1週間
**作業量**: 約1.5時間
**対象**: アダプタ約12個、共通ハンドラ約5個、チェック項目2個、その他約5個

**全体作業量**: 約4.5時間（作成2.5時間 + 品質チェック2時間）

---

### 3.3 品質保証

#### 5段階プロセス

1. **作成**: AIエージェントが知識ファイルを作成します
2. **自動チェック**: スキーマ準拠性、JSON構文チェックを行います
3. **サンプリングレビュー**: 20%のファイルを人間がレビューします
   - ランダムサンプリング: 各カテゴリから均等に選択します
   - 重点サンプリング: ハンドラ、主要ライブラリは必須でレビューします
4. **Nablarch有識者レビュー**: 重要ファイルの正確性検証を行います
5. **フィードバックループ**: 問題点を次回作成時に反映します

#### 品質基準

- 仕様の網羅性（必須/オプション/デフォルト値）
- 制約の網羅性（「重要」「注意」「警告」を全て反映）
- コード例が動作する最小形であること
- 出典（official_doc_urls）を全ての情報に付与すること
- 対象外情報（Jakarta Batch等）を含まないこと

---

## 4. 参考資料

### 4.1 公式ドキュメント

| カテゴリ | URL |
|---------|-----|
| **Nablarch解説書** | https://nablarch.github.io/docs/LATEST/doc/ |
| **Nablarchバッチ** | https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/batch/nablarch_batch/index.html |
| **RESTful Webサービス** | https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/web_service/rest/index.html |
| **標準ハンドラ** | https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/handlers/index.html |
| **ライブラリ** | https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/libraries/index.html |
| **テスティングFW** | https://nablarch.github.io/docs/LATEST/doc/development_tools/testing_framework/index.html |
| **システム開発ガイド** | https://fintan.jp/page/252 |
| **Nablarchパターン集** | https://fintan.jp/page/252/2/ |
| **Nablarchアンチパターン** | https://fintan.jp/page/252/5/ |

### 4.2 リポジトリ

| 対象 | GitHub URL |
|------|-----------|
| **nablarch-example-batch** | https://github.com/nablarch/nablarch-example-batch |
| **nablarch-example-rest** | https://github.com/nablarch/nablarch-example-rest |

---

## まとめ

### 本設計書で定義したこと

1. **代行業務10個**と優先度を明確化しました
2. **知識タイプ3つを定義**し、作成単位を決定しました（約60個）
3. **検索アーキテクチャ**を設計しました（keyword + intent並列、関連度3段階）
4. **TOON形式インデックス**を採用しました（30-60%トークン削減）
5. **セクション単位の抽出**でコンテキスト管理します（上位10セクション ≈ 5,000トークン）
6. **4フェーズの実装計画**を策定しました（総作業時間約4.5時間）

### 次のアクション

1. フェーズ1を実施します（バッチフレームワーク知識の拡充 ≈ 1.5時間）
2. 仮説検証を行います（代行精度と工数削減の実測）
3. 効果測定後、フェーズ2以降へ進みます

---

**以上**
