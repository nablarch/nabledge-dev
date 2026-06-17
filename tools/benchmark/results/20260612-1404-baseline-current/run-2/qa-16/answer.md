**結論**: `UniversalDao.exists()` で SQL_ID を指定してデータ存在チェックを行うには、`UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` を使用します。戻り値は `boolean` で、データが存在すれば `true` が返ります。

**根拠**:

まず、存在確認用の SELECT SQL をファイルに定義します。SQLファイルのパスはエンティティクラスから導出されます（例：`sample.entity.User` クラスの場合、クラスパス配下の `sample/entity/User.sql`）。

```sql
-- ユーザー存在確認SQL
CHECK_USER_EXISTS =
SELECT
    user_id
FROM
    user
WHERE
    user_id = :userId
```

次に、Java コードで `exists()` を呼び出します。

**バインド変数なし（全件存在チェック）の場合:**

```java
boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS");
```

**バインド変数あり（条件付き存在チェック）の場合:**

```java
// 検索条件をBeanに設定する
User condition = new User();
condition.setUserId(targetUserId);

boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS", condition);
if (exists) {
    // データが存在する場合の処理
}
```

別クラスのSQLファイルを参照する場合は `#` を使って指定できます:

```java
// sample/entity/Member.sql の CHECK_EXISTS を参照する場合
boolean exists = UniversalDao.exists(User.class, "sample.entity.Member#CHECK_EXISTS", condition);
```

`exists()` は内部で検索用SQLを変換して使用するため、個別に件数取得用・存在確認用のSQLを作成する必要はなく、通常の SELECT SQL をそのまま使用できます。

**注意点**:
- SQL_ID に `#` を含めることで任意のSQLファイルのSQLを参照できますが、指定が煩雑になるため基本は `#` なしの指定（エンティティクラスからSQLファイルパスを導出する方式）を使用してください。
- `exists()` は `countBySqlFile()` と同様に、検索用SQLを変換して実行するため、COUNT文を別途作成する必要はありません。

参照: javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18, component/libraries/libraries-universal-dao.json:s7