**結論**: `UniversalDao.exists` は SQL_ID（第2引数）を指定することでデータ存在チェックができ、バインド変数が必要な場合は第3引数に条件 Bean を渡します。データが存在すれば `true`、存在しなければ `false` を返します。

**根拠**:

バインド変数なし（SQL で条件が固定の場合）:
```java
boolean exists = UniversalDao.exists(User.class, "CHECK_EXISTS");
```

バインド変数あり（条件を動的に指定する場合）:
```java
// 条件 Bean を作成する
User condition = new User();
condition.setUserId("U001");

boolean exists = UniversalDao.exists(User.class, "CHECK_EXISTS", condition);
```

メソッドシグネチャ:
```java
// バインド変数なし
public static boolean exists(Class<T> entityClass, String sqlId)

// バインド変数あり
public static boolean exists(Class<T> entityClass, String sqlId, Object params)
```

SQL_ID に対応する SQL ファイルは、第1引数の Bean クラスから自動導出されます。たとえば `User.class` が `sample.entity.User` の場合、SQLファイルのパスはクラスパス配下の `sample/entity/User.sql` となります。別クラスの SQL ファイルを使いたい場合は `#` 記法を使います:

```java
// sample/entity/UserCheck.sql の CHECK_EXISTS を使う場合
UniversalDao.exists(SomeEntity.class, "sample.entity.UserCheck#CHECK_EXISTS", condition);
```

内部では検索用の SQL を変換して件数チェックを行い、存在すれば `true` を返します。

**注意点**:
- `exists` に渡す SQL は検索用 SQL として記述し、件数チェック用 SQL を個別に作成する必要はありません（内部で変換されます）

参照: javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18, component/libraries/libraries-universal-dao.json:s7