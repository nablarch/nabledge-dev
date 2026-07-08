# qa-16 — run-1

## 質問

UniversalDao.exists で SQL_ID を指定してデータ存在チェックをする方法を教えてください

## 回答

**結論**: `UniversalDao.exists` は第2引数に SQL_ID を指定でき、対象データが存在する場合は `true`、存在しない場合は `false` を返します。バインド変数がある場合は第3引数にパラメータ Bean を渡します。

**根拠**:

`exists` メソッドには2つのオーバーロードがあります。

① バインド変数なし（全件チェック）:
```java
boolean result = UniversalDao.exists(User.class, "CHECK_EXISTS");
```

② バインド変数あり（条件付きチェック）:
```java
// 検索条件Beanを準備
User condition = new User();
condition.setUserId("U001");

boolean result = UniversalDao.exists(User.class, "CHECK_EXISTS", condition);
```

SQLファイルはエンティティクラスのパスから導出されます。`User.class` が `sample.entity.User` の場合、クラスパス配下の `sample/entity/User.sql` が使用されます。別クラスのSQLファイルを参照したい場合は `#` を使って指定できます:

```java
// sample/entity/Member.sql の CHECK_EXISTS を使用
UniversalDao.exists(User.class, "sample.entity.Member#CHECK_EXISTS", condition);
```

`exists` の内部では検索用SQLを件数取得用に変換して実行するため、個別にカウント用SQLを作成する必要はありません。

**注意点**:
- SQLファイル内には通常の `SELECT` 文を記述します（`exists` 専用のSQL構文は不要）
- `#` を使った SQL_ID 指定は指定が煩雑になるため、基本は使用しないことが推奨されています

参照: javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc-nablarch-common-dao-UniversalDao.json:s18, libraries-universal-dao.json:s7

## 参照ナレッジ

- [exists](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md#exists) (s17)
- [exists](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md#exists) (s18)
- [任意のSQL(SQLファイル)で検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#任意のsqlsqlファイルで検索する) (s7)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts. It describes the `exists(Class, String)` method (バインド変数なし overload) and the `exists(Class, String, Object)` method (バインド変数あり overload) with concrete code examples. Both expected facts about the two overloaded `exists` methods are clearly conveyed, achieving complete coverage. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to use UniversalDao.exists with SQL_ID for data existence checking. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.91 | NG | The score is 0.91 because the actual output incorrectly states the SQL ID as 'CHECK_EXISTS' when referencing 'sample.entity.Member#FIND_BY_NAME', whereas the retrieval context clearly indicates the SQL ID should be 'FIND_BY_NAME' when using the '#' notation. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「SQL_IDを指定してバインド変数なしでデータ存在チェックを行うexists(Class, String)メソッドがある」は回答の「① バインド変数なし（全件チェック）: `boolean result = UniversalDao.exists(User.class, "CHECK_EXISTS");`」に含まれている。参照事実「SQL_IDとバインド変数を指定してデータ存在チェックを行うexists(Class, String, Object)メソッドがある」は回答の「② バインド変数あり（条件付きチェック）: `boolean result = UniversalDao.exists(User.class, "CHECK_EXISTS", condition);`」に含まれている。 |
| answer_relevancy | OK | 回答は質問（UniversalDao.exists で SQL_ID を指定したデータ存在チェックの方法）に直接答えており、バインド変数なし・ありの2つのオーバーロード、SQLファイルパスの導出規則、`#` 記法による別SQLファイル参照まで網羅している。的外れな内容は含まれていない。 |
| faithfulness | OK | DeepEval は回答コード例の `CHECK_EXISTS` を誤りとして NG 判定したが、これは false positive である。ナレッジ（libraries-universal-dao.md）の `#` 記法説明例では `FIND_BY_NAME` を SQL ID として使っているが、回答は独立したサンプルとして `CHECK_EXISTS` を使っており、SQL ID 名が異なるだけで仕様の説明（`#` の左がファイルパス・右が SQL ID）は一致している。回答の内容はナレッジの記述と矛盾しない。 |

### 参照事実（expected_facts）

- SQL_IDを指定してバインド変数なしでデータ存在チェックを行うexists(Class, String)メソッドがある
- SQL_IDとバインド変数を指定してデータ存在チェックを行うexists(Class, String, Object)メソッドがある
