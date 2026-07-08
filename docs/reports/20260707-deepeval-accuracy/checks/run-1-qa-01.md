# qa-01 — run-1

## 質問

大量データを検索するとメモリが足りなくなる。1件ずつ読み込む方法はないか？

## 回答

**結論**: `UniversalDao.defer()` メソッドを使用して遅延ロードを有効にする。これにより内部でサーバサイドカーソルが使われ、1件ずつ読み込むことができる。

**根拠**:

`UniversalDao.defer()` を検索の直前に呼び出すことで遅延ロードが有効になる。`DeferredEntityList` はサーバサイドカーソルを使用するため、全件をメモリに展開せずにループ処理できる。

```java
// try-with-resourcesを使ったclose呼び出し。
// DeferredEntityListはダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**注意点**:
- `DeferredEntityList#close()` を必ず呼び出すこと。呼び出さないとサーバサイドカーソルのリソースがリークする（try-with-resources を使うこと）
- カーソルオープン中にトランザクション制御が行われると、使用するRDBMSによってはカーソルがクローズされる場合がある。遅延ロードを使用した大量データ処理中にトランザクション制御を行うと、クローズ済みのカーソルを参照しエラーとなる可能性があるため注意すること

参照: libraries-universal-dao.json:s9

## 参照ナレッジ

- [検索結果を遅延ロードする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果を遅延ロードする) (s9)
- [Nablarchバッチアプリケーションで使用するデータリーダ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションで使用するデータリーダ) (s7)
- [Jakarta Batchに準拠したバッチアプリケーションで遅延ロードを行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/adapters/adapters-doma-adaptor.md#jakarta-batchに準拠したバッチアプリケーションで遅延ロードを行う) (s10)
- [データベースアクセス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md#データベースアクセス) (s4)
- [検索範囲を指定してSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#検索範囲を指定してsqlを実行する) (s15)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both key facts from the Expected Output: (1) it clearly states that `UniversalDao.defer()` is used to enable deferred (lazy) loading, and (2) it explicitly mentions that `DeferredEntityList#close()` must be called, with a warning about resource leaks if not called, and recommends using try-with-resources. Both expected facts are present and correctly represented without contradiction. |
| answer_relevancy | 0.95 | 0.92 | NG | The score is 0.92 because the response effectively addresses the question about memory issues when searching large data and how to load records one at a time. However, it loses a few points due to the inclusion of an internal metadata reference (libraries-universal-dao.json:s9) that is not directly relevant to answering the user's question. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「UniversalDao.deferメソッドで遅延ロードを使用する」は回答の「`UniversalDao.defer()` メソッドを使用して遅延ロードを有効にする」に含まれている。参照事実「DeferredEntityListのcloseメソッドを呼び出す必要がある」は回答の「`DeferredEntityList#close()` を必ず呼び出すこと」に含まれている。 |
| answer_relevancy | NG | 回答の末尾に「参照: libraries-universal-dao.json:s9」というシステム内部のメタデータ参照が含まれており、これはユーザーの質問（大量データを1件ずつ読み込む方法）に対して無関係な内部情報である。実質的な説明内容（UniversalDao.defer()の使い方、DeferredEntityList、注意点）はすべて質問に直接回答しているが、この内部参照タグが不要な情報として混入している。 |
| faithfulness | OK | ナレッジMD（libraries-universal-dao.md）の「検索結果を遅延ロードする」セクションと照合すると、(1)UniversalDao.defer()を検索直前に呼び出す、(2)内部でサーバサイドカーソルを使用、(3)DeferredEntityList#close()を必ず呼び出す、(4)try-with-resourcesの使用例、(5)トランザクション制御中のカーソルクローズへの注意、いずれも回答の内容がナレッジの記述と一致しており矛盾はない。コードサンプルもナレッジのものと同一である。 |

### 参照事実（expected_facts）

- UniversalDao.deferメソッドで遅延ロードを使用する
- DeferredEntityListのcloseメソッドを呼び出す必要がある
