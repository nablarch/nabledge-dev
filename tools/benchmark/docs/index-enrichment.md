# Index Enrichment

`index-llm.md` に検索の手がかりとなるキーワードを付記し、AI-1 (search) の
ページ発見能力を上げるためのワークフロー。

**本版はセクション単位 TF (IDF なし) 方式。** 旧ページ単位 TF-IDF 方式は
ページの「看板語」しか抽出できず、複数ページで特徴語となる共通概念
(`バージョンアップ` / `後方互換` / `@Published` 等) が埋もれる問題が
あった。セクション単位 TF では各セクションの焦点語がそのまま残る。

## 検索フロー全体像（前提）

AI-1 の検索は 2 経路で構成される:

1. **index-llm.md 経路（意味マッチ）**: AI-1 が index を読んで `selections` を返す
2. **term_queries 経路（本文 grep）**: スクリプトが質問文から機械抽出した語で
   全ページ本文を grep し、ヒットしたセクションを selections にマージ

本ワークフローは **1 の index-llm.md 経路** を強化するもの。
2 の term_queries は **ASCII 識別子** (CamelCase / camelCase / @Annotation)
のみを機械抽出するので、それら識別子を index-llm.md に追記しても重複する
だけで価値が増えない。

そのため **index-llm.md に入れるのは日本語の概念語** に限定する。
具体的には、**各セクションの本文で頻出する日本語特徴語** (セクション内 TF
上位語から stoplist 除外したもの)。

日本語は term_queries では扱わない。質問の複合語は本文と表記がズレ、
短い語は generic すぎて noise になるため。

## 目的

AI-1 は `index-llm.md` を読んでユーザー質問に合うページを選ぶ。現状の index
はページタイトルとセクションタイトルしか持たないため、質問文のキーワードが
それらに出てこないページは発見されない。

本ワークフローは、各セクションの本文から「そのセクションを特徴づけるキーワード」
を TF ランキングで抽出し、汎用語を stoplist で除外した上で index に付記する。

## index 形式 (セクション単位配置)

```
[handlers-transaction_management_handler] トランザクション制御ハンドラ
  s1:ハンドラクラス名 — トランザクション管理 / コールバック / ロールバック
  s2:モジュール一覧
  s3:制約 — 配置順序 / DbConnectionManagementHandler
  s5:特定の例外の場合にトランザクションをコミットさせる — コミット / ロールバック
  s6:トランザクション終了時に任意の処理を実行したい — コールバック / TransactionEventCallback
  s7:アプリケーションで複数のトランザクションを使用する — transactionName
```

### 配置ルール

各セクションについて:

- **セクション本文を tokenize → TF 計算** (そのセクション内での登場回数)
- **stoplist (汎用語、section_df が高い語) を除外**
- **識別子 (@Annotation/CamelCase/camelCase) も除外** (term_queries 経路担当)
- **残った語の TF 上位 N 語** をそのセクション行末に `— ` で付記
- 短いセクションで unique 語が少なければ N 未満でもよい

### なぜセクション単位か

ページ単位 TF-IDF は **各ページ内でスコアを最大化する語** (看板語) を
抽出する。結果、複数ページにまたがる中核概念 (`バージョンアップ` など) は
どのページでも TF は高いが IDF で削られ、最終的に index に入らない。

セクション単位 TF は **各セクション内での頻度** を直接使う。汎用語は
stoplist で落とすので IDF の代わりになり、セクション固有に頻出する
中核概念 (例: s4 で `後方互換性 14回 / アノテーション 8回 /
バージョンアップ 5回`) をそのまま拾える。

### ヒットなし時

セクションによっては TF 上位語が全て stoplist に落ち、付記キーワードが
0 になることがある。それは正常 (セクションタイトルで既に意味が取れる場合)。

## 対象バージョン

開発起点は v6 だが、すべてのスクリプトは `--version` オプションで
他バージョン (v5 / v1.4 / v1.3 / v1.2) に切替可能。

## ディレクトリ構成

```
tools/benchmark/
  classify_terms.py           # セクション単位 TF 抽出
  build_index.py              # index-llm.md 生成
  search_next.py              # AI-1 検索 + term_queries 機械抽出
  build_term_stopset.py       # term_queries 用 df ベース stopset (ASCII 識別子用)
  data/
    index-keywords-ja.json    # セクション × 採用キーワード配列 (生成物)
    index-stoplist-ja-v6.json # 日本語汎用語 stoplist (手動判定)
    term_stopset-v6.json      # ASCII 識別子用 df stopset (term_queries 側)
  docs/
    index-enrichment.md       # 本ドキュメント
```

## 全体フロー

```
1. stoplist の決定 (build_term_stopset.py の日本語版相当)
   - 全セクションを走査し、日本語 4+ 字語の section_df を集計
   - section_df の高い順に帯で区切って人間判定
       ↓
2. セクション単位 TF 抽出 (classify_terms.py)
   - 各セクションで tokenize → TF 計算
   - stoplist / 識別子パターンで除外
   - セクションごとに TF 上位 N 語を残す
       ↓
3. index 生成 (build_index.py)
   - 各セクション行末に採用キーワードを付記
   - index-llm.md を再生成
       ↓
4. 効果測定 (benchmark run.py --search-only / search_coverage.py)
```

**重要**:
- stoplist 判定は TF 抽出の前に必ず完了させる
- `@Annotation / CamelCase / camelCase` は index-llm.md に入れない。
  これらは term_queries 経路でカバーされる
- stoplist と term_stopset (ASCII 用) は別ファイル。役割が違う

## 抽出パターン (classify_terms.py)

正規表現で以下を抽出し、TF の対象トークンとする。

| パターン | 例 | 分類 |
|---|---|---|
| `@Annotation` | `@Published` `@UseToken` | index 対象外 (term_queries で拾う) |
| CamelCase 2-hump | `DataReader` `BatchAction` | index 対象外 (term_queries で拾う) |
| camelCase プロパティ | `connectionFactory` `transactionName` | index 対象外 (term_queries で拾う) |
| カタカナ 4字以上 | `トランザクション` `バリデーション` | TF 対象 |
| 漢字 4字以上 | `公開API` `並列実行` | TF 対象 |
| 漢字+カタカナ混合 4字以上 | `暗号化処理` `悲観ロック` | TF 対象 |

**注**: 3字以下の語は採用しない。3字以下は一般語が多く、4字以上の複合語で
代替できる (例: `暗号化` は `暗号化処理` `暗号化機能` で拾える)。

**term_queries 経路との役割分担**:
- 識別子 (@Annotation / CamelCase / camelCase) は質問文に直接書かれること
  が多く、機械抽出してページ本文 grep するのが確実
- 日本語・漢字の概念語は、質問と本文で表記が揺れやすい (質問「レート制限」/
  本文「流量制御」など)。この層で意味の橋渡しをするのが index-llm.md の役割

## stoplist の決定プロセス

### 方針

- **TF のみ採用** (IDF は不要)。ストップリストで汎用語を除去する前提なので、
  IDF で「複数セクションにまたがる語」を打ち消すとむしろ逆効果
  (`トランザクション` が複数セクションで特徴語化するのを許容したい)
- **ノイズ定義**: 複数セクションにまたがる汎用語 (`ファイル` / `プロパティ` /
  `ハンドラ` 等) のみ。セクション固有に頻出する語 (例: s8 で
  `リクエストパラメータ` 14回) はノイズではない
- **判定基準**: section_df (その語が出るセクション数)
- **目安**: section_df ≥ 75 前後 (~22 語) が汎用語ライン。section_df ≥ 50 まで
  広げるとトランザクション (67) / バリデーション (66) / セッション (52) など
  中核用語が落ちるので過剰

### 判定手順

1. 全セクションを走査し、日本語 4+ 字語の section_df を集計
2. section_df の高い順に帯で区切って人間判定:
   - section_df ≥ 100 (~14 語): 明確に汎用 → 全員 stoplist 入り
   - section_df 50〜99 (~31 語): 境界帯、中核用語 (トランザクション等) を残す
   - section_df 30〜49 (~43 語): 大半は固有用語、例外のみ stoplist
   - section_df < 30: 残す (固有性が高い)
3. 判定結果を `.work/00307/stoplist-judgment.md` に残す
4. 最終 stoplist: `tools/benchmark/data/index-stoplist-ja-v6.json`

### 判定基準

× (stoplist 入り) を付ける代表パターン:

- 文書メタ語 / 自己参照: 「本機能」「記載」「補足」「見出し一覧」
- 文書構造の副産物: 「外部サイト」「リンク先」
- 過度に広い一般語: 「設定」「使用」「処理」「ファイル」「プロパティ」

○ (残す) の基準:

- (A) 開発者が Nablarch に関する質問を書くときに、その語またはごく近い語を使う可能性がある
- (B) セクション固有の主題と意味的に結びついている
- (C) 複数セクションで共通の中核概念 (例: `トランザクション` `バリデーション`) は
  むしろ残す。IDF で消さない方針

### 3 エージェント並列方式

スコア帯ごとの判定は、メインエージェントの単独判定に加え、サブエージェントを
3 並列で起動して独立判定させることで精度を上げる。

フローはページ単位 TF-IDF 版と同一:
1. データ準備 (対象帯の全語 + section_df + snippet)
2. 3 サブエージェントに並列投げ (Task ツール、同一プロンプト)
3. 結果集計 (3-0 / 2-1 / 1-2 / 0-3)
4. メインエージェントのスクリーニング
5. ユーザー最終確認 (迷う語のみ)

### サブエージェント判定プロンプト (テンプレート)

```
あなたは Nablarch フレームワークの知識検索インデックスを審査する判定者です。

## 背景
Nablarch 日本語ドキュメントから生成された知識ベースがあり、各ページには
ID とタイトルが付いています。各ページは複数セクションに分かれています。
ユーザー（Nablarch を使う日本人開発者）の自然言語の質問に対し、下流の
AI エージェントが index-llm.md を読んで関連セクションを最大10件選びます。
index-llm.md の各セクション行は次の形式です。

  sN:セクションタイトル — キーワード1 / キーワード2 / ...

あなたの役割は、与えられた「汎用語候補」を stoplist (index に載せない)
に入れるべきか (×) 残すべきか (○) を独立に判定することです。

## 判定基準

× (stoplist 入り) = 「ほぼ全ページ/全セクションに出る汎用語で、
特定のセクションを特徴づけない」語。

○ (残す) の条件、以下のいずれかを満たす:
- (A) Nablarch の中核概念 (例: トランザクション、バリデーション、セッション)
  複数セクションに出てもセクション固有の文脈を示すことが多い
- (B) 特定のセクション群でのみ頻出し、文脈識別に有効
- (C) 開発者が質問で自然に使う語

× を付ける代表パターン:
- 文書メタ語: 「本機能」「記載」「補足」
- 過度に広い一般語: 「設定」「使用」「処理」「ファイル」「プロパティ」「クラス名」
- 文書構造の副産物: 「外部サイト」「リンク先」

## 入力

以下は判定対象の語の配列です (section_df 付き):

{{TERMS_JSON}}

## 出力

各語について、以下の JSON 配列を返してください:

[
  {"term": "...", "verdict": "○" または "×",
   "reason": "1文。どの基準 (A)(B)(C) または ×パターンに該当するかを明示",
   "confidence": "high" / "medium" / "low"},
  ...
]
```

## コマンド

```bash
# section_df ランキング生成 (stoplist 判定用)
python3 tools/benchmark/build_stoplist_ja.py --version 6 \
    --out /tmp/section-df-v6.json

# セクション単位 TF 抽出
python3 tools/benchmark/classify_terms.py --version 6 \
    --stoplist tools/benchmark/data/index-stoplist-ja-v6.json \
    --top-n 10 \
    --out tools/benchmark/data/index-keywords-ja.json

# index-llm.md 生成
python3 tools/benchmark/build_index.py --version 6 \
    --keywords tools/benchmark/data/index-keywords-ja.json
```

## 効果測定

```bash
# 検索のみ実行 (AI-1 だけ回す、AI-3 / judge はスキップ)
python3 tools/benchmark/run.py --variant next --search-only

# カバー率測定 (expected_sections との比較)
python3 tools/benchmark/search_coverage.py --run-dir .tmp/search-only-XXXX
```

目標: ページ発見率が現在の baseline を上回ること。特にページ単位 TF-IDF で
拾えなかった「複数ページにまたがる中核概念」系のケース (review-10 の
`about-nablarch-versionup_policy`, impact-01 の `@Published` など) で
selections が通るようになること。

## term_queries (機械抽出、本文 grep 経路)

`search_next.py` は AI-1 の `selections` 応答に加え、質問文から機械抽出した
**識別子** で本文 grep を行う。抽出対象は ASCII のみ:

| パターン | 例 |
|---|---|
| `@Annotation` (4+ 字) | `@Published` `@UseToken` |
| CamelCase 2-hump (4+ 字) | `TransactionManagementHandler` |
| camelCase (4+ 字) | `connectionFactory` `transactionName` |

**日本語は対象外**。実測ですべて次のいずれかに落ちるため:
- 質問の複合語 (`明細レコード` `夜間バッチ`) は本文に出ない (表記ズレ)
- 抽出できた短い語 (`レコード` `チェック` `クライアント`) は generic すぎて
  noise にしかならず、per-term/total cap を食い尽くす

日本語概念語は **index-llm.md の section-level keyword** で扱う
(役割分担を崩さない)。

term_queries は AI-1 に生成させず **スクリプトが機械抽出する**。これで:
- AI-1 のプロンプトから term_queries 生成タスクを削除できる
- 決定的で再現性が高い
- AI-1 が抽出語を選ぶ際のバイアスが入らない

grep 側のフィルタ (ASCII 識別子用 term_stopset-v6.json):
- df_pct が 20% を超える語は grep 対象から外す (候補爆発を防ぐ)
  ASCII 識別子のみなので v6 では 2 語 (`artifactId`, `groupId`)
- per-term ヒット上限、total ヒット上限で selections に merge する量を制御

## 注意事項

- **ベンチマークシナリオに合わせて採用語を選ばない** (出来レース防止)。
  「現場の開発者が質問しそうか」という抽象基準で判断する
- **hints フィールドは使わない**。knowledge JSON にはセクションごとの `hints`
  があるが、これはベンチマークシナリオに合わせて調整された疑いがあり、
  現場の質問には効かない可能性がある
- **セクション単位 TF を採用**。ページ単位 TF-IDF はページの看板語しか
  抽出できず、複数ページ共通の中核概念が埋もれる問題があったため、セクション
  単位に切り替え。IDF は不要 (stoplist で汎用語を除外するため)
- **index-llm.md と term_queries の役割分担を崩さない**。同じ語を両方に
  入れると冗長で、AI-1 の attention を分散させる

## 他バージョンへの展開

**共通して流用できるもの:**

- `term_stopset` (ASCII 識別子の df ベース) — パターン自動許可なので
  `build_term_stopset.py --version N` で再生成
- 日本語 stoplist の大部分 — Nablarch 中核概念の汎用語 (`ファイル` /
  `プロパティ` / `処理` 等) はバージョン間で共通

**バージョン固有のため再判定が必要なもの:**

- section_df の高い語の一部 (Jakarta EE 移行関連など v5→v6 固有のもの)

**展開手順:**

1. `build_stoplist_ja.py --version N` で section_df ランキング生成
2. 既存 v6 stoplist をベースに、バージョン固有の追加語のみ判定
3. `classify_terms.py --version N` → `build_index.py --version N` で index 生成
