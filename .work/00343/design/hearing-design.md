# ヒアリング 設計書

**Status**: Draft
**Date**: 2026-05-20

## 目的

ユーザーの質問が曖昧な場合に、処理方式を特定するための質問を行い、意味検索の精度を向上させる。
また、ユーザーの目的（purpose）を自動推論して意味検索のカテゴリ選定バイアスに使用する。

## 位置づけ

```
qa.md
  ├── qa/hearing.md     ← ここ
  ├── semantic-search.md
  ├── read-sections.sh
  ├── qa/answer.md
  └── qa/verify.md
```

ヒアリングは意味検索の前段。質問からprocessing_typeとpurposeを特定し、意味検索に渡す。

## 方式

### 概要

```
質問 → 分類（skip / ask）→ [askの場合: ユーザーに質問] → hearing_answer出力
```

LLMが質問を分析し、処理方式が明示されていれば自動抽出、曖昧であればユーザーに質問する。ユーザーの回答が不明確な場合は処理方式が特定できるまで対話を続ける。

purposeは常に自動推論（ユーザーに質問しない）。

### なぜ処理方式のヒアリングが必要か

Nablarchは処理方式（Web / REST API / バッチ等）ごとに異なる実装パターンを持つ。同じ概念（バリデーション、エラーハンドリング、DB登録等）でも処理方式によって使うハンドラ・API・設定が異なる。

ベンチマーク26件の分析:
- 質問中に処理方式が明示: 8件（should_skip）→ 自動抽出可能
- 処理方式が不明で回答に影響: 7件（must_ask）→ ヒアリング必須
- 処理方式を聞くと精度向上: 11件（nice_to_ask）→ ヒアリングが望ましい

### 分類ロジック（processing_type）

LLMが質問を読み、以下の順で判定する。

**skip（ヒアリング不要）**:
- 質問に処理方式が明示されている（「REST APIで」「バッチで」「Web画面の」「JSPの」等）
- 質問が処理方式に依存しない横断的機能（テスティングフレームワーク、多言語化、ロギング設定等）

**ask（ヒアリング必要）**:
- 質問の回答が処理方式によって変わり得る、かつ処理方式が質問から特定できない

### 出力（hearing_answer）

hearing.mdの出力はhearing_answer。分類（skip/ask）は内部状態であり、下流には渡さない。

```json
{
  "processing_type": "ウェブアプリケーション",
  "purpose": "実装したい"
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| processing_type | string \| null | 処理方式。横断的機能の場合はnull |
| purpose | string | ユーザーの目的（7択固定） |

- processing_type（skip）: 質問から自動抽出
- processing_type（ask）: ユーザーの回答から設定
- processing_type（横断的機能）: null
- purpose: 常に自動推論（ユーザーへの質問なし）

### 処理方式の特定

分類ロジックでは、質問中の明示キーワードを2グループの静的リストと照合する。利用可能な処理方式一覧は`{processing_types}`としてプロンプトに注入する（呼び出し側がindex.mdから取得）。

**グループ1（正式名称・公式略称）**: 処理方式の正式名称またはNablarchドキュメントで使われる略称。
- ウェブアプリケーション、Webアプリ、Web画面
- RESTfulウェブサービス、REST API、RESTful、REST
- Nablarchバッチ、バッチアプリケーション
- Jakartaバッチ
- テーブルをキューとして使ったメッセージング
- HTTPメッセージング
- MOMメッセージング

**グループ2（技術要素→処理方式マッピング）**: Nablarch内で1つの処理方式にのみ存在する技術要素。
- JSP、HIDDENストア、セッション変数、セッションストア、CSRF → ウェブアプリケーション
- リソースクラス、JAX-RS → RESTfulウェブサービス
- requestPath（バッチ起動引数の文脈で）→ Nablarchバッチ
- ItemReader、ItemWriter、Chunk → Jakartaバッチ

**skipの場合**: キーワードが1つの処理方式のみを指す場合、その処理方式を抽出する。複数の処理方式に一致する場合はaskに切り替える。

**askの場合**: `{processing_types}`の処理方式一覧からユーザーに選択肢を提示する。

質問フォーマット例（v6の場合）:
```
お使いの処理方式を教えてください。
- ウェブアプリケーション
- RESTfulウェブサービス
- Nablarchバッチ
- 都度起動バッチ
- Jakartaバッチ
- HTTPメッセージング
- MOMメッセージング
```

### purposeの推論

purposeはユーザーに質問せず、LLMが質問文から自動推論する。以下の7択から1つを選ぶ。

**7択カテゴリ**:
1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. 実装パターン・サンプルを参考にしたい
7. セキュリティ対応したい

**推論シグナル**:
- 「仕組み」「とは」「動作」「理解」「概要」→ 仕組み・動作を理解したい
- 「エラー」「例外」「不具合」「原因」「調査」→ 不具合・エラーを調査したい
- 「テスト」「テストコード」「テストケース」→ テストを書きたい
- 「バージョンアップ」「移行」「マイグレーション」「アップグレード」→ バージョンアップしたい
- 「サンプル」「パターン」「例を見たい」「参考」→ 実装パターン・サンプルを参考にしたい
- 「セキュリティ」「脆弱性」「認証」「認可」→ セキュリティ対応したい
- （上記いずれにも該当しない）→ **実装したい**（デフォルト）

**purpose → 優先カテゴリ対応（意味検索へのバイアスとして使用）**:
| purpose | 優先カテゴリ |
|---------|------------|
| 実装したい | processing-pattern/*, component/libraries |
| 仕組み・動作を理解したい | component/handlers, component/libraries, about/about-nablarch |
| 不具合・エラーを調査したい | component/handlers, component/libraries, processing-pattern/* |
| テストを書きたい | development-tools/testing-framework, component/libraries |
| バージョンアップしたい | about/migration, releases/releases, about/release-notes |
| 実装パターン・サンプルを参考にしたい | guide/nablarch-patterns, guide/biz-samples, processing-pattern/* |
| セキュリティ対応したい | check/security-check, component/handlers, processing-pattern/* |

purposeはprocessing_typeのように回答を決定するものではなく、カテゴリ選定の優先順位バイアスとして機能する。誤推論時の影響は軽微（順位が変わるが回答候補は変わらない）。

## プロンプト構成

部品は2プロンプトに分離:
- `tools/benchmark/components/prompts/hearing-classify.md` — 分類（skip/ask）+ skip時のhearing_answer抽出（purpose推論含む）
- `tools/benchmark/components/prompts/hearing-extract.md` — ask時、ユーザー回答からhearing_answer構成（purpose推論含む）

スキルワークフロー: `workflows/qa.md` に直接インライン（qa/hearing.md は不使用）

### 入力

- 質問文
- 利用可能な処理方式一覧（`{processing_types}`、index.mdのprocessing-patternカテゴリから呼び出し側が取得して注入）

### 出力

hearing_answer（processing_type + purpose）。意味検索の入力として使用。

### 手順

**hearing-classify.md**（Step 1+2共通の処理に対応）:
1. 質問を読み、明示キーワードリスト（グループ1・2）と照合する
2. キーワードが見つかり1つの処理方式のみを指す → skip（その処理方式）
3. キーワードが複数の処理方式を指す → ask
4. キーワードなし → 横断的機能か判定:
   - 横断的機能 → skip（processing_type = null）
   - それ以外 → ask
5. purposeを推論（質問文のシグナルから7択を選択）
6. skipの場合: processing_typeとpurposeを抽出してhearing_answerを出力
7. askの場合: hearing_answer = null を返す（呼び出し側がユーザーに質問）

**hearing-extract.md**（askの場合のみ）:
1. ユーザーの回答（選択した処理方式）を受け取る
2. purposeを推論（元質問のシグナルから7択を選択）
3. 元質問 + ユーザー回答からprocessing_typeとpurposeを構成してhearing_answerを出力

### トレース

以下の情報をトレースとして記録する:

- classification: skip / ask
- reason: 分類理由（1行）
- matched_keywords: 質問中で処理方式と照合されたキーワード（skipの場合）
- candidates: askの場合にユーザーに提示した選択肢一覧
- purpose_signal: purposeの推論根拠（キーワードまたは「デフォルト」）

### CC/GHC差異

| 環境 | ユーザーへの質問方法 |
|---|---|
| CC (Claude Code) | AskUserQuestion ツール |
| GHC (GitHub Copilot) | テキストで質問し、ユーザーの返信を待つ |

hearing.mdは環境に依存しない形で「ユーザーに質問する」と記述する。ツール選択はLLMが環境に応じて判断する。

## シミュレーション

### 評価対象

ヒアリングは2つの能力を評価する:

1. **分類精度**: 質問をskip/askに正しく分類できるか
2. **抽出精度**: processing_typeとpurposeを正しく抽出/構成できるか

### シミュレーション方式

分類と抽出を1回のLLM呼び出しで評価する。

```
入力: 質問文のみ（hearing_answerなし）
LLM: 分類（skip/ask）+ skip時のprocessing_type/purpose推論
比較: expected_hearing、hearing_answer（ground truth）と照合
```

askと分類した場合のユーザー対話シミュレーション:
```
入力: 質問文 + シナリオのhearing_answer.processing_type（ユーザー回答として注入）
LLM: processing_type設定 + purpose推論
比較: hearing_answer（ground truth）と照合
```

### 評価メトリクス

| メトリクス | 定義 | 判定基準 | ゲート |
|---|---|---|---|
| classification | skip/askの分類一致 | expected_hearingと比較。should_skip→skip、must_ask/nice_to_ask→ask | PASS/FAIL判定に使用 |
| processing_type | 処理方式の一致 | ground truthと完全一致 | PASS/FAIL判定に使用 |
| purpose | 目的カテゴリの一致 | ground truthと完全一致（7択固定） | 情報提供のみ（ゲートなし） |

classificationはシミュレーション内部の評価軸。hearing.mdの出力（hearing_answer）には含まれない。

purposeは7択固定のため厳密な一致判定が可能。ただしprocessing_typeが正しければpurposeの微差は意味検索の優先順位に影響するのみで、回答候補自体は変わらない。

### must_ask vs nice_to_ask の扱い

シミュレーションではmust_askとnice_to_askを区別しない。両方とも「askが正解」として評価する。理由: nice_to_askは「聞いた方がよい」であり、聞かないことはエラーではないが、聞く方が精度が上がるためaskを推奨する。

should_skipをaskに分類した場合は**許容**する（不要なヒアリングが発生するがエラーではない）。
must_askをskipに分類した場合は**FAIL**とする（必要なヒアリングが欠落し精度に影響する）。

| expected | 実際の分類 | 判定 |
|---|---|---|
| should_skip | skip | PASS |
| should_skip | ask | PASS（余分だが無害） |
| must_ask | ask | PASS |
| must_ask | skip | FAIL |
| nice_to_ask | ask | PASS |
| nice_to_ask | skip | PASS（改善余地あり） |

## 根拠

### ターン数の方針

ヒアリングの目的は処理方式の特定。Nablarchの処理方式は有限の選択肢（4-7種）であり、典型的には1回の質問で特定できる。ただしターン数は固定しない — ユーザーの回答が不明確な場合は追加質問を行い、明確な場合は1ターンで完了する。

### processing_typeとpurposeの2軸である理由

- **processing_type**: 知識ページへのルーティングに必須。異なる処理方式は異なるファイルに格納されており、間違った処理方式で検索すると全く異なる（誤った）回答が生成される。
- **purpose**: 意味検索のカテゴリ優先順位バイアス。同じ質問でも「実装したい」と「仕組みを理解したい」では参照すべき知識カテゴリが異なる。purposeが誤っても候補セット全体は変わらず、優先順位が変わるのみ。

### purposeを常にskipとする理由

purposeは質問文のシグナルから高精度で推論可能（デフォルト「実装したい」で大多数の質問をカバー）。
また、purposeの誤推論時の影響はprocessing_typeと比較して軽微（カテゴリ優先順位の変化のみ）。
processing_typeのヒアリングに加えてpurposeを別途質問することはUXコストに対してROIが低い。

### nice_to_askもaskとする理由

ベンチマーク分析で、nice_to_askシナリオでもヒアリング回答があることでStage1の精度が向上することを確認している（意味検索v4: 97.4%達成時、全シナリオでhearing_answer注入済み）。不要なヒアリング（1ターン）のUXコストより、検索精度の向上が重要。
