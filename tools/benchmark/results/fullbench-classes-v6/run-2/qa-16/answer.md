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