**結論**: `UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` を呼び出すことで、SQL_ID を指定したデータ存在チェックができます。存在すれば `true` を返します。

**根拠**:

SQLファイルに対象データの検索SQLを定義し、そのSQL IDを `exists` メソッドに渡します。

**バインド変数なしの場合:**
```java
boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS");
```

**バインド変数ありの場合:**
```java
// 検索条件Beanを用意する
User condition = new User();
condition.setUserId("U0001");

boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS", condition);
```

SQLファイルのパスは、第1引数に指定したBeanクラスから導出されます。例えば `sample.entity.User` の場合、SQLファイルのパスはクラスパス配下の `sample/entity/User.sql` となります。別のBeanのSQLファイルを使いたい場合は、SQL IDに「#」を含めて指定します:

```java
// sample/entity/MemberCheck.sql の CHECK_EXISTS SQL IDを使う場合
boolean exists = UniversalDao.exists(User.class, "sample.entity.MemberCheck#CHECK_EXISTS", condition);
```

内部的には検索用SQLが件数取得（または存在確認）SQLへ変換されて実行されます。

**注意点**: `exists` メソッドはバインド変数なし版（`exists(Class, String)`）とバインド変数あり版（`exists(Class, String, Object)`）の2種類があります。条件パラメータが不要な場合は前者、検索条件を渡す場合は後者を使用してください。

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  任意のSQL(SQLファイル)で検索する