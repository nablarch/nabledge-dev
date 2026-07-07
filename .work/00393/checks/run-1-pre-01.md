# pre-01 — run-1

## 質問

Nablarchバッチアプリケーションはどのように起動しますか？-requestPathの書き方を教えてください

## 回答

**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスを `java` コマンドで直接起動します。`-requestPath` には「実行するアクションのクラス名/リクエストID」という書式で指定します。

**根拠**:

起動コマンドは以下の形式です。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

必須オプションは以下の3つで、いずれか1つでも欠けると即座に異常終了します（終了コード = 127）。

| オプション | 内容 |
|-----------|------|
| `-diConfig` | システムリポジトリの設定ファイルのパスを指定する |
| `-requestPath` | 実行するアクションとリクエストIDを指定する |
| `-userId` | ユーザIDを設定する（`user.id` としてセッションコンテキスト変数に格納）|

`-requestPath` の書式は以下のとおりです。

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

起動後の処理の流れ:
1. `Main` クラスがハンドラキューを実行する
2. データリーダ（DataReader）が入力データを1件ずつ読み込む
3. ディスパッチハンドラ（DispatchHandler）が `-requestPath` で指定されたリクエストパスをもとに処理すべきアクションクラスを特定する
4. アクションクラスがデータレコード1件ごとの業務ロジックを実行する
5. 処理対象データがなくなるまで繰り返し、最終的にステータスコードをプロセス終了コードに変換して終了する

**注意点**:
- リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを実行するプロセスを複数起動する場合、このリクエストIDが識別子となります。

参照: nablarch-batch-architecture.json:s2, component/handlers/handlers-main.json:s3

## 参照ナレッジ

- [リクエストパスによるアクションとリクエストIDの指定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#リクエストパスによるアクションとリクエストidの指定) (s2)
- [アプリケーションを起動する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-main.md#アプリケーションを起動する) (s3)
- [Nablarchバッチアプリケーションの構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションの構成) (s1)
- [Nablarchバッチアプリケーションの処理の流れ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションの処理の流れ) (s3)
- [バッチアプリケーションの起動方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md#バッチアプリケーションの起動方法) (s1)
- [アプリケーション起動に任意のオプションを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-main.md#アプリケーション起動に任意のオプションを設定する) (s4)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both facts from the Expected Output. It explicitly states that Nablarch batch applications are launched directly via the `java` command (standalone execution), and it explains that `-requestPath` specifies the action class name and request ID in the format 'アクションのクラス名/リクエストID'. Both key facts are addressed clearly and with equivalent meaning. |
| answer_relevancy | 0.95 | 0.82 | NG | The score is 0.82 because the actual output addresses the core questions about how to launch a Nablarch batch application and how to write -requestPath, but it also includes explanations of internal processing details such as data reader behavior, action class business logic execution, and process repetition/exit code conversion. These internal processing descriptions are not directly relevant to the questions asked about startup methods and -requestPath syntax, which prevents the score from being higher. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「javaコマンドから直接起動するスタンドアロンアプリケーションとして実行する」は回答の「`nablarch.fw.launcher.Main` クラスを `java` コマンドで直接起動します」に含まれている。参照事実「-requestPathコマンドライン引数でアクションのクラス名とリクエストIDを指定する」は回答の「`-requestPath` には「実行するアクションのクラス名/リクエストID」という書式で指定します」に含まれている。 |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- javaコマンドから直接起動するスタンドアロンアプリケーションとして実行する
- -requestPathコマンドライン引数でアクションのクラス名とリクエストIDを指定する
