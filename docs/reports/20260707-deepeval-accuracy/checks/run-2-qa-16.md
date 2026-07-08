# qa-16 — run-2

## 質問

UniversalDao.exists で SQL_ID を指定してデータ存在チェックをする方法を教えてください

## 回答

**結論**: `UniversalDao.exists` メソッドにエンティティクラスとSQL IDを指定することで、SQLファイルを使ったデータ存在チェックができます。

**根拠**:

2種類のオーバーロードが用意されています。

**バインド変数なしの場合**:

```java
boolean result = UniversalDao.exists(User.class, "FIND_BY_NAME");
```

**バインド変数ありの場合**（条件を指定してチェックする場合）:

```java
User condition = new User();
condition.setName("Taro");

boolean result = UniversalDao.exists(User.class, "FIND_BY_NAME", condition);
```

- 第1引数: エンティティクラス（SQLファイルのパス導出に使用）
- 第2引数: SQL ID（SQLファイル内のSQL IDを文字列で指定）
- 第3引数（任意）: バインド変数（検索条件をBeanとして渡す）
- 戻り値: データが存在すれば `true`、存在しなければ `false`

**SQLファイルのパスについて**:

SQL IDは、エンティティクラスのFQCNからパスを導出します。`sample.entity.User` クラスを指定した場合、SQLファイルのパスはクラスパス配下の `sample/entity/User.sql` となります。別クラスのSQLファイルを参照したい場合は、`"sample.entity.Member#FIND_BY_NAME"` のように `#` 区切りでSQLファイルのパスとSQL IDを明示できます。

**注意点**: `exists` は検索用のSQLを内部で変換して件数チェックを行います。SELECTするSQLを用意するだけで、専用の件数取得SQLを作成する必要はありません。

参照: javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18, component/libraries/libraries-universal-dao.json:s7

## 参照ナレッジ

- [exists](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md#exists) (s17)
- [exists](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md#exists) (s18)
- [任意のSQL(SQLファイル)で検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#任意のsqlsqlファイルで検索する) (s7)
- [検索結果をBeanにマッピングできる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果をbeanにマッピングできる) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both expected facts clearly. It describes the exists(Class, String) method (no bind variables) and the exists(Class, String, Object) method (with bind variables/conditions), with code examples for each. Both facts from the Expected Output checklist are present in the Actual Output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to use UniversalDao.exists with SQL_ID for data existence checking. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「exists(Class, String)メソッドがある」は回答の「boolean result = UniversalDao.exists(User.class, "FIND_BY_NAME");」に含まれており、参照事実「exists(Class, String, Object)メソッドがある」は回答の「boolean result = UniversalDao.exists(User.class, "FIND_BY_NAME", condition);」に含まれている |
| answer_relevancy | OK | 回答は質問（UniversalDao.existsでSQL_IDを指定してデータ存在チェックをする方法）に直接答えており、2種類のオーバーロード、コード例、引数説明、SQLファイルパスの導出方法、#区切り指定、内部変換の注意点まで、すべて質問に関連する内容のみで構成されている。的外れな内容は含まれていない。 |
| faithfulness | OK | 回答の各主要事実はナレッジMDと一致している。2種類のオーバーロード（exists(Class,String)とexists(Class,String,Object)）はJavadocに記載済み。SQLファイルパスの導出ルール（sample.entity.User → sample/entity/User.sql）はlibraries-universal-dao.md 117-118行と一致。#区切り指定の説明もlibraries-universal-dao.md 119-126行と一致。「検索用のSQLを内部で変換して件数チェックを行う」はJavadoc 337行「検索用のSQLを変換して使用する」と一致。ナレッジとの矛盾は見当たらない。 |

### 参照事実（expected_facts）

- SQL_IDを指定してバインド変数なしでデータ存在チェックを行うexists(Class, String)メソッドがある
- SQL_IDとバインド変数を指定してデータ存在チェックを行うexists(Class, String, Object)メソッドがある
