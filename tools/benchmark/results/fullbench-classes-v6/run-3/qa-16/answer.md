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