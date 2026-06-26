**結論**: `UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` を使用します。SQL_IDを指定してデータの存在チェックを行い、存在すれば `true`、存在しなければ `false` を返します。

**根拠**:

2つのオーバーロードが提供されています。

**バインド変数なしの場合**:

```java
public static boolean exists(Class<T> entityClass, String sqlId)
```

**バインド変数ありの場合**:

```java
public static boolean exists(Class<T> entityClass, String sqlId, Object params)
```

**実装例**:

```java
// バインド変数なし（検索条件が固定の場合）
boolean exists = UniversalDao.exists(User.class, "EXISTS_USER");

// バインド変数あり（検索条件をBeanで指定する場合）
User condition = new User();
condition.setId(123L);
boolean exists = UniversalDao.exists(User.class, "EXISTS_USER", condition);
```

**SQL_IDの指定方法**はSQLファイル検索（`findAllBySqlFile`等）と同じルールに従います:

- デフォルト形式: `"SQL_ID"` — Beanのクラス(`entityClass`)からSQLファイルパスを導出し、SQL IDを指定
  - 例: `entityClass` が `sample.entity.User` の場合、`sample/entity/User.sql` 内の `EXISTS_USER` を使用
- クロスファイル形式: `"パッケージ.クラス名#SQL_ID"` — 別のBeanに紐づくSQLファイルのSQL IDを指定

```java
// 別クラスのSQLファイルを使う場合
boolean exists = UniversalDao.exists(GoldUser.class, "sample.entity.Member#EXISTS_MEMBER", condition);
```

参照: javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc-nablarch-common-dao-UniversalDao.json:s18, libraries-universal-dao.json:s7