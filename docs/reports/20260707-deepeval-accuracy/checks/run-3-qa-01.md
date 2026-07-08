# qa-01 — run-3

## 質問

大量データを検索するとメモリが足りなくなる。1件ずつ読み込む方法はないか？

## 回答

**結論**: `UniversalDao.defer().findAllBySqlFile(...)` を使って検索結果を `DeferredEntityList` として受け取ることで、サーバサイドカーソルによる1件ずつの遅延ロードが実現できます。

**根拠**:

遅延ロードは、検索時に `UniversalDao#defer` メソッドを先に呼び出すだけで使用できます。

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

遅延ロードを使用すると、ユニバーサルDAOとしては1件ずつロードします。内部でサーバサイドカーソルを使用しているため、`DeferredEntityList#close` メソッドを呼び出してリソースを解放する必要があります（try-with-resources を使うことで確実に解放できます）。

なお、メモリ使用量はJDBCのフェッチサイズによっても変わります。詳細はデータベースベンダー提供のマニュアルを参照してください。

**注意点**:
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされます。大量データの処理中にトランザクション制御（コミット等）を行った場合、クローズ済みのカーソルを参照してエラーになる可能性があります。データベースベンダーのマニュアルに従ってカーソルの挙動を調整するか、ページングで回避してください。

参照: libraries-universal-dao.json:s9, javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s27

## 参照ナレッジ

- [検索結果を遅延ロードする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果を遅延ロードする) (s9)
- [defer](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md#defer) (s27)
- [フィールドの詳細](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-DeferredEntityList.md#フィールドの詳細) (s1)
- [データベースアクセス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md#データベースアクセス) (s4)
- [Nablarchバッチアプリケーションで使用するデータリーダ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションで使用するデータリーダ) (s7)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts: (1) it explicitly mentions using `UniversalDao.defer()` method to achieve deferred/lazy loading, and (2) it explicitly states that `DeferredEntityList#close` method must be called to release resources, with additional guidance on using try-with-resources. Both facts from the Expected Output checklist are fully covered. |
| answer_relevancy | 0.95 | 0.93 | NG | The score is 0.93 because the response largely addresses the question of how to load records one at a time to avoid memory issues with large data queries. However, it loses a small amount of relevance by referring to the database vendor's manual for fetch size details, which is a slight tangent from the core question being asked. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「UniversalDao.deferメソッドで遅延ロードを使用する」は回答の「UniversalDao.defer().findAllBySqlFile(...)」および「遅延ロードは、検索時に `UniversalDao#defer` メソッドを先に呼び出すだけで使用できます」に含まれている。参照事実「DeferredEntityListのcloseメソッドを呼び出す必要がある」は回答の「`DeferredEntityList#close` メソッドを呼び出してリソースを解放する必要があります」に含まれている。 |
| answer_relevancy | OK | 回答は「大量データで1件ずつ読み込む方法」という質問に直接答えており、遅延ロードの使い方・コード例・リソース解放・注意点がすべて質問の主旨に沿っている。DeepEvalが「やや余談」と指摘したJDBCフェッチサイズの言及は、ナレッジ（libraries-universal-dao.md 147〜148行目）に「JDBCのフェッチサイズによってメモリの使用量が変わる。フェッチサイズの詳細は、データベースベンダー提供のマニュアルを参照」と明記されており、メモリ問題を質問したユーザーへの重要な補足情報として的外れではない。 |
| faithfulness | OK | 回答の全内容がナレッジ（libraries-universal-dao.md の「検索結果を遅延ロードする」セクション）と一致している。遅延ロードはUniversalDao#deferを先に呼び出すだけ、内部でサーバサイドカーソルを使用、DeferredEntityList#closeでリソース解放が必要、トランザクション制御中のカーソルクローズリスクへの警告、フェッチサイズはベンダーマニュアル参照——これらすべてがナレッジに記載されており矛盾は存在しない。 |

### 参照事実（expected_facts）

- UniversalDao.deferメソッドで遅延ロードを使用する
- DeferredEntityListのcloseメソッドを呼び出す必要がある
