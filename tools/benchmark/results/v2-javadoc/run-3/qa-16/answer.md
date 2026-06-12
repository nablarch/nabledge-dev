Step 5〜8: 回答を生成・検証します。

---

**結論**: `UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` を使用することで、任意のSQLによるデータ存在チェックができます。戻り値は `boolean` で、1件以上存在すれば `true` が返ります。

**根拠**:

SQLファイルの作成ルールは `findAllBySqlFile` と同様です（SQLファイルのパスはエンティティクラスから導出されます）。

```sql
-- クラスパス配下の sample/entity/User.sql に定義する例
-- SQL_ID: EXISTS_BY_NAME
EXISTS_BY_NAME =
select
  user_id
from
  user
where
  user_name = :userName
```

バインド変数なしの場合:

```java
boolean exists = UniversalDao.exists(User.class, "EXISTS_BY_NAME");
```

バインド変数ありの場合（条件Beanを第3引数に渡す）:

```java
// 条件Beanを準備する
User condition = new User();
condition.setUserName("山田太郎");

boolean exists = UniversalDao.exists(User.class, "EXISTS_BY_NAME", condition);
```

別クラスのSQLファイルを使いたい場合は、SQL_IDに `#` を含めて指定します:

```java
boolean exists = UniversalDao.exists(
    User.class, "sample.entity.Member#EXISTS_BY_NAME", condition);
```

**注意点**:
- `exists` メソッドは内部的に検索用SQLを変換して実行するため、個別に件数取得用SQLを作成する必要はありません。
- SQLファイルは検索結果をマッピングするエンティティクラスと同じパスに配置します（`sample.entity.User` クラスなら `sample/entity/User.sql`）。

参照: `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17`, `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18`, `component/libraries/libraries-universal-dao.json:s7`

---