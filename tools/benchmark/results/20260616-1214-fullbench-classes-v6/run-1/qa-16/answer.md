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