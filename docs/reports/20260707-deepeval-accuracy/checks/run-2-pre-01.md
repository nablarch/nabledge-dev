# pre-01 — run-2

## 質問

Nablarchバッチアプリケーションはどのように起動しますか？-requestPathの書き方を教えてください

## 回答

**結論**: NablarchバッチアプリケーションはJavaの`main`クラス（`nablarch.fw.launcher.Main`）を`java`コマンドで直接起動します。起動時に必須の引数として `-diConfig`、`-requestPath`、`-userId` の3つを指定する必要があります。

**根拠**: 

起動コマンドの基本形は以下のとおりです:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

各オプションの意味は次のとおりです:

| オプション | 必須 | 説明 |
|---|---|---|
| `-diConfig` | 必須 | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 必須 | 実行するアクションのクラス名とリクエストID |
| `-userId` | 必須 | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

**`-requestPath` の書式**:

```bash
-requestPath=アクションのクラス名/リクエストID
```

具体例:

```bash
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- アクションのクラス名は完全修飾クラス名（FQCN）で指定します
- リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを複数プロセスで起動する場合に区別するために使われます

**注意点**: 3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`）のうちいずれかが欠けていた場合、アプリケーションは即座に異常終了します（終了コード = 127）。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3

## 参照ナレッジ

- [リクエストパスによるアクションとリクエストIDの指定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#リクエストパスによるアクションとリクエストidの指定) (s2)
- [アプリケーションを起動する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-main.md#アプリケーションを起動する) (s3)
- [Nablarchバッチアプリケーションの処理の流れ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションの処理の流れ) (s3)
- [アプリケーション起動に任意のオプションを設定する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-main.md#アプリケーション起動に任意のオプションを設定する) (s4)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both facts from the Expected Output checklist. First, it explicitly states that the batch application is launched via the `java` command directly (standalone execution with `nablarch.fw.launcher.Main`), covering the first expected fact. Second, it thoroughly explains the `-requestPath` argument specifying the action class name and request ID, covering the second expected fact. Both facts are present and well-elaborated in the Actual Output. |
| answer_relevancy | 0.95 | 0.86 | NG | The score is 0.86 because the response mostly addresses how to launch a Nablarch batch application and how to write -requestPath, but it loses points for including irrelevant details about the internal behavior of -userId (session context variable) and the exit code 127 on abnormal termination, neither of which are relevant to the question asked. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「javaコマンドから直接起動するスタンドアロンアプリケーションとして実行する」は回答の「Javaの`main`クラス（`nablarch.fw.launcher.Main`）を`java`コマンドで直接起動します」に含まれている。参照事実「-requestPathコマンドライン引数でアクションのクラス名とリクエストIDを指定する」は回答の「-requestPath の書式」節および具体例に含まれている。 |
| answer_relevancy | OK | 回答は質問（バッチアプリケーションの起動方法と-requestPathの書き方）に直接答えている。DeepEvalがNG理由として挙げた「-userIdのセッションコンテキスト変数詳細」と「終了コード127」は、知識ドキュメントの「アプリケーションを起動する」セクションに含まれる起動説明の一部であり、必須オプションを説明する文脈で書かれているため質問と無関係ではない。的外れな内容は含まれていない。 |
| faithfulness | OK | 回答の全ての事実がナレッジと一致している。nablarch.fw.launcher.Mainクラス名、javaコマンド直接起動、3つの必須オプション（-diConfig/-requestPath/-userId）、コマンド例、-requestPathの書式（「アクションのクラス名/リクエストID」）と具体例、-userIdのセッションコンテキスト変数user.id、欠落時の終了コード127 — すべてhandlers-main.mdおよびnablarch-batch-architecture.mdの記述と矛盾なく一致している。 |

### 参照事実（expected_facts）

- javaコマンドから直接起動するスタンドアロンアプリケーションとして実行する
- -requestPathコマンドライン引数でアクションのクラス名とリクエストIDを指定する
