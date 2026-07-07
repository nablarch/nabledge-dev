# pre-01 — run-3

## 質問

Nablarchバッチアプリケーションはどのように起動しますか？-requestPathの書き方を教えてください

## 回答

**結論**: NablarchバッチアプリケーションはJavaコマンドで`nablarch.fw.launcher.Main`クラスを起動する。`-requestPath`には`アクションのクラス名/リクエストID`の書式で実行対象を指定する。

**根拠**:

起動コマンドの実行例:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

フレームワークの動作に必要な3つのオプションはすべて必須。いずれか1つでも欠けると終了コード127で即座に異常終了する。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパスを指定 |
| `-requestPath` | 実行するアクションとリクエストIDを指定 |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納される） |

**`-requestPath`の書式**:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- `アクションのクラス名`は完全修飾クラス名またはパッケージ相対クラス名
- `リクエストID`は各バッチプロセスの識別子。同一アクションクラスを複数プロセスで起動する場合に区別するために使用する

**注意点**: 3つの必須オプションのうち1つでも欠けている場合、終了コード127で即座に異常終了する。

参照: handlers-main.json:s3, nablarch-batch-architecture.json:s2

## 参照ナレッジ

- [アプリケーションを起動する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-main.md#アプリケーションを起動する) (s3)
- [リクエストパスによるアクションとリクエストIDの指定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#リクエストパスによるアクションとリクエストidの指定) (s2)
- [アプリケーション起動に任意のオプションを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-main.md#アプリケーション起動に任意のオプションを設定する) (s4)
- [例外及びエラーに応じた処理内容](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-main.md#例外及びエラーに応じた処理内容) (s5)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both facts from the Expected Output. It mentions that the batch application is launched using the Java command (standalone application), and it explains the -requestPath argument format specifying the action class name and request ID. Both key facts are present and well-elaborated in the Actual Output. |
| answer_relevancy | 0.95 | 0.93 | NG | The score is 0.93 because the response is mostly relevant to explaining how to start a Nablarch batch application and how to write -requestPath. However, it slightly loses points for including an implementation detail about storing userId in a session context variable, which is unrelated to the startup process or -requestPath syntax. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「javaコマンドから直接起動するスタンドアロンアプリケーションとして実行する」は回答の「NablarchバッチアプリケーションはJavaコマンドで`nablarch.fw.launcher.Main`クラスを起動する」に含まれている。参照事実「-requestPathコマンドライン引数でアクションのクラス名とリクエストIDを指定する」は回答の「-requestPathの書式」セクションで明記されている。 |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- javaコマンドから直接起動するスタンドアロンアプリケーションとして実行する
- -requestPathコマンドライン引数でアクションのクラス名とリクエストIDを指定する
