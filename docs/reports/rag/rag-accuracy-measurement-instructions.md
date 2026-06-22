# RAG精度実測 作業指示書

## 0. この作業の目的

Nabledgeの代わりにRAG（ベクトル検索）を使った場合、検索精度がどのくらいになるかを実測する。Nabledgeは同じ34シナリオで全パス済み。RAGが全パスに届くか、特にNablarch固有語（処理方式・クラス名）で外さないかを、推測でなく数字で確かめる。

**最重要**: フラットに測る。RAGを不当に低くも高くも見せない。下記の設計判断を厳守し、勝手に変えない。変える必要が出たら理由を添えて報告し、判断を仰ぐ。事実・試算・推測を区別して報告する。

---

## 1. あなた（依頼者）が用意するもの

CCをBedrock（東京リージョン）で使っているため、AWSアカウント・認証情報・リージョン設定は既にある。**追加で必要なのは埋め込みモデルのアクセス許可だけ。**

| 用意するもの | 説明 |
|---|---|
| Cohere Embed Multilingual のアクセス許可 | CCで使うClaudeとは別モデル。Bedrockのアクセスはモデルごとに個別許可のため、これは別途必要 |

### アクセス許可の取り方
1. AWSコンソール → Bedrock → 左メニュー「Model access」
2. 「Cohere Embed Multilingual」を探して「Request access」
3. 数分で「Access granted」になる（無料、利用した分だけ課金）

> 既存のCC用認証情報（`aws configure` または環境変数、東京リージョン `ap-northeast-1`）をそのまま使う。
>
> 費用の目安: 全約9,529チャンク＋34質問の埋め込みで **$1未満**。ベクトルDB(FAISS)・実行はローカルで無料。

---

## 2. 実行環境

- 普通のPC（CPUのみ、GPU不要）。FAISSは約9,529ベクトル程度なら一瞬（数MB、メモリに余裕）。
- Python 3.x
- インストール: `pip install boto3 faiss-cpu numpy`
- 対象は **v6のみ**

---

## 3. 登場人物とフロー

```
① 知識ファイル（知識JSON 935ファイル → 約9,529チャンク）
② 埋め込みモデル（Bedrock Cohere Multilingual）… 文章→1024次元ベクトル
③ ベクトルDB（FAISS・ローカル）… ベクトルを保存し近い順に検索
④ 評価スクリプト（自作）… 34シナリオで採点

準備（1回）: ①を②でベクトル化し③に保存
評価（34回）: 質問を②でベクトル化→③で上位k件取得→正解が入ったか④で採点
```

---

## 4. リポジトリと対象データ

```bash
git clone --depth 1 https://github.com/nablarch/nabledge.git
git clone --depth 1 https://github.com/nablarch/nabledge-dev.git
```

- 知識ソース: `nabledge/plugins/nabledge-6/skills/nabledge-6/knowledge/` 配下の知識JSON（935ファイル）
- シナリオ: `nabledge-dev/tools/benchmark/scenarios/qa.json`（34シナリオ）

---

## 5. 設計判断（確定値・厳守）

### 5-1. チャンク単位
知識JSONの構造は `{id, title, content, no_knowledge_content, sections:[{id, title, content, level}]}`。

- `sections` が空でない場合: **各セクションを1チャンク**とする。チャンクのテキストは `{ページtitle} > {section title}\n{section content}`
- `sections` が空の場合: ページ全体（title + content）を1チャンク
- `no_knowledge_content == true` のファイルは除外
- 各チャンクに `file`（knowledge/からの相対パス）と `section_id`（例 `s3`、単一ページは `__page__`）を保持
- 理由: docs MDを自前で切ると分割設計に推測が混じる。JSONは既にセクション分割済みで、Nabledgeと同じ粒度になり公平。

**チャンクは全部で約9,529個**（935ファイルから生成。ファイル数ではなくチャンク数で数える）。

**入力上限への対応（必須）**: Cohere Embedの入力上限は512トークン（日本語で約1,500〜2,000字）。実データには2,000字を超えるチャンクが**約212件**ある。上限超過分が黙って切り捨てられると、そのチャンクのベクトルが不完全になり不当にmissする（＝RAGを不当に低く見せる）。対応:
- 1チャンクが上限を超える場合、**重複なしで複数サブチャンクに分割**し、同じ `file:section_id` を全サブチャンクに付与する。
- 検索でサブチャンクのどれかが上位kに入れば、その `file:section_id` がヒットしたとみなす。
- 分割が発生したチャンク数をレポートに記録する。

### 5-2. 埋め込みモデル
- **Bedrock Cohere Embed Multilingual**（多言語特化）、東京リージョン
- **モデルIDは実行時にBedrockで確認すること**。`cohere.embed-multilingual-v3` が基本だが、東京リージョンではクロスリージョン推論プロファイル（`apac.` 接頭辞等）が必要な場合がある。`aws bedrock list-foundation-models` 等で利用可能なIDを確認してから使う。**IDが見つからないからといって別系統のモデル（Titan等）に勝手に変えない**。多言語特化モデルを使うこと自体は厳守。
- Cohereの `input_type` を正しく使う: **チャンク側は `search_document`、質問側は `search_query`**
- 1024次元
- 理由: Nablarchは日本語。多言語特化モデルで本番に近い精度を測る。Titan系は英語最適化で日本語が劣るため使わない。

### 5-3. k（取得件数）
- **k=20 を主**（Nabledgeが実際に読むセクション数の上限20に一致）
- **k=10 を感度分析**として併記
- 理由: kはNabledgeの意味検索の代替。実セクション数に合わせ「同じ件数で正解が含まれる率」を公平に比較。

### 5-4. メタデータフィルタ（3条件で測る）
シナリオの `when.hearing_answer.processing_type`（処理方式）を使う。実際の値は4種のみ: `Nablarchバッチ` / `RESTfulウェブサービス` / `ウェブアプリケーション` / `null`（横断的）。

**処理方式 → ディレクトリ対応表（確定値・厳守）**:

| processing_type | 中核ディレクトリ |
|---|---|
| Nablarchバッチ | `processing-pattern/nablarch-batch/` |
| RESTfulウェブサービス | `processing-pattern/restful-web-service/` |
| ウェブアプリケーション | `processing-pattern/web-application/` |
| null | フィルタなしと同じ扱い |

- **条件(a) フィルタなし**: 全チャンクを検索対象（素のRAG）
- **条件(b) 正しいフィルタ**: 処理方式が指定されている場合、次に絞る。
  - 含める: 上表の中核ディレクトリ ＋ 横断カテゴリ `component/libraries`・`component/handlers`・`component/adapters`・`check/*`
  - 除外: 他方式固有の `processing-pattern/`（例: バッチ指定時は `restful-web-service/`・`web-application/` 等を除外）
  - 根拠: Nabledgeの検索が「異なる処理方式はスキップ、横断ページは残す」のと同じ絞り方。
- **条件(c) 素朴なフィルタ（対照）**: 中核ディレクトリのみに絞る（横断カテゴリを含めない）
  - これは構造的に多くの正解を除外する（例: ウェブアプリケーションの正解は全て横断カテゴリにあり、この条件だと全miss）。「フィルタ設計の巧拙がスコアを左右する」ことを示すための対照。

`processing_type` が null のシナリオはフィルタなしと同じ扱い。

### 5-5. 正解判定
- シナリオの `then.must[].section`（例 `component/libraries/libraries-universal-dao.json:s3`）が正解。正解sectionは全34シナリオで計44件あり、**全て対応するチャンクが実在することは確認済み**。
- 上位k件のチャンク（`file:section_id`）と照合し、シナリオ単位で:
  - **pass**: must の全sectionが上位kに含まれる
  - **partial**: 一部のみ
  - **miss**: 1件も含まれない
- `must[].section` が無いシナリオ（アウトオブスコープ）は**2件**。これは別集計・除外し、**評価対象は32件**。除外したことをレポートに明記。

---

## 6. 出力（レポート）

### 6-1. スコア
条件の組み合わせ（フィルタ a/b/c × k=20/10）ごとに:
- pass / partial / miss の件数と率
- シナリオ別一覧（id, 質問, 処理方式, 判定, 正解が上位何位か）

### 6-2. 必ず分析する観点
- 処理方式を質問文に書いていないシナリオでのスコア（素のRAGの弱点が出る箇所）
- 頻出固有クラス名（UniversalDao等）を含む質問でのスコア
- フィルタ条件 a/b/c でスコアがどう変わるか（前処理の効果）
- k=20 と k=10 の差

### 6-3. レポート構成
- 結論 → 評価基準 → 比較（測定値を中立に） → 根拠と次の一歩
- 各記述に【事実】【試算】【推測】を付す
- 一般エンジニア向けに、RAG・埋め込み・コサイン類似度を初出時に簡潔に説明
- Nabledgeの全パス（既知）と並べて、RAGが要件（全パス）に届くかを判定

---

## 7. 進め方の注意

- 推測で進めない。設計判断で迷ったら報告して仰ぐ。
- 実物（JSON・シナリオ）を全件確認してから集計する。部分grepで済ませない。
- 正解sectionが全てチャンクとして実在するか、集計前に突合する（測定バグの排除）。
- スコアが極端に良い/悪い場合は実装ミスを疑い、自己検証してから報告する。
- 中間生成物（チャンク・ベクトル・スコア）は再現可能な形で残す。

---

## 8. 成果物

1. RAG構築・実測スクリプト（再実行可能）
2. スコア集計レポート（6-3の構成、MDファイル）
3. シナリオ別判定の一覧（表）
