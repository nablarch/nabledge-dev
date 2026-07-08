**結論**: `UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` メソッドを使用する。第1引数にエンティティクラス、第2引数にSQL_IDを指定すると、そのSQLでデータが存在するかどうかを `boolean` で取得できる。

**根拠**:

バインド変数なしの場合:
```java
boolean result = UniversalDao.exists(User.class, "FIND_BY_NAME");
```

バインド変数ありの場合:
```java
// 検索条件を設定したBeanを渡す
User condition = new User();
condition.setName("山田太郎");
boolean result = UniversalDao.exists(User.class, "FIND_BY_NAME", condition);
```

SQL_IDは `findAllBySqlFile` 等と同じ形式で指定する。SQLファイルはエンティティクラスのパッケージ・クラス名から導出される（`sample.entity.User` → `sample/entity/User.sql`）。異なるSQLファイルを参照したい場合は `#` を使う。

```java
// 別クラスのSQLファイルを参照する場合
boolean result = UniversalDao.exists(User.class, "sample.entity.Member#CHECK_EXISTS", condition);
```

メソッドの内部では、検索用のSQLを変換して存在チェックに使用する。

**注意点**:
- `exists` の第3引数（`params`）には、SQLファイル内のバインド変数に対応するBeanを渡す
- `exists` は存在すれば `true`、0件なら `false` を返す（例外は送出しない）

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  任意のSQL(SQLファイル)で検索する
- class UniversalDao
  .claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md
  exists