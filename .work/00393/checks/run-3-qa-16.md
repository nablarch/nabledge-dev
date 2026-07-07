# qa-16 — run-3

## 質問

UniversalDao.exists で SQL_ID を指定してデータ存在チェックをする方法を教えてください

## 回答

**結論**: `UniversalDao.exists` に SQL_ID を指定することで、SQLファイルを使ったデータ存在チェックが行えます。バインド変数なしの `exists(entityClass, sqlId)` とバインド変数ありの `exists(entityClass, sqlId, params)` の2つのオーバーロードがあります。

**根拠**:

バインド変数なしで存在チェックする場合：

```java
boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS");
```

バインド変数ありで存在チェックする場合：

```java
// 検索条件をBeanに設定する
User condition = new User();
condition.setName("taro");

boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS", condition);
```

**SQLファイルのパス解決**は `findAllBySqlFile` と同じルールに従います。

- `"CHECK_USER_EXISTS"` → 第1引数のクラス（例: `sample.entity.User`）から `sample/entity/User.sql` を導出し、その中の `CHECK_USER_EXISTS` を使用
- `"sample.entity.Member#CHECK_USER_EXISTS"` → `sample/entity/Member.sql` 内の `CHECK_USER_EXISTS` を使用（SQLを別ファイルに集約したい場合）

**注意点**:
- `exists` メソッドは内部で検索用SQLを変換して実行します。個別に件数取得用SQLを作成する必要はありません（`countBySqlFile` と同様の仕組み）。
- SQLファイルは検索結果をマッピングするクラスのパッケージ構造から導出されるため、第1引数に指定するクラスのパッケージに注意してください。

参照: javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc-nablarch-common-dao-UniversalDao.json:s18, libraries-universal-dao.json:s7

## 参照ナレッジ

- [任意のSQL(SQLファイル)で検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#任意のsqlsqlファイルで検索する) (s7)
- [使用方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#使用方法) (s5)
- [exists](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md#exists) (s17)
- [exists](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md#exists) (s18)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts from the checklist. It explicitly mentions the `exists(entityClass, sqlId)` overload (バインド変数なしの exists) and the `exists(entityClass, sqlId, params)` overload (バインド変数ありの exists), with code examples demonstrating both `UniversalDao.exists(User.class, "CHECK_USER_EXISTS")` and `UniversalDao.exists(User.class, "CHECK_USER_EXISTS", condition)`. Both expected facts about the two method signatures are fully covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to use UniversalDao.exists with SQL_ID for data existence checks. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「exists(Class, String)メソッドがある」は回答の「バインド変数なしの `exists(entityClass, sqlId)`」および `UniversalDao.exists(User.class, "CHECK_USER_EXISTS")` のコード例に含まれている。参照事実「exists(Class, String, Object)メソッドがある」は回答の「バインド変数ありの `exists(entityClass, sqlId, params)`」および `UniversalDao.exists(User.class, "CHECK_USER_EXISTS", condition)` のコード例に含まれている。 |
| answer_relevancy | NG | 回答末尾に「参照: javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc-nablarch-common-dao-UniversalDao.json:s18, libraries-universal-dao.json:s7」という内部参照記法がユーザー向け回答に含まれており不適切。 |
| faithfulness | OK | ナレッジ内容と矛盾なし。javadoc の s17（exists(Class, String)）・s18（exists(Class, String, Object)）の記述と回答内容が一致しており、hallucination は確認されない。 |

### 参照事実（expected_facts）

- SQL_IDを指定してバインド変数なしでデータ存在チェックを行うexists(Class, String)メソッドがある
- SQL_IDとバインド変数を指定してデータ存在チェックを行うexists(Class, String, Object)メソッドがある
