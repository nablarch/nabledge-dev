**結論**: `UniversalDao.exists` にSQL_IDを指定してデータ存在チェックを行うには、`UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` を使用します。

**根拠**:

`UniversalDao.exists` メソッドは2つのオーバーロードを提供します。

**バインド変数なしの場合:**
```java
boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS");
```

**バインド変数ありの場合（条件を指定して存在確認）:**
```java
// 検索条件を持つBeanを用意する
User condition = new User();
condition.setUserId("U001");

boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS", condition);
```

SQLファイルの配置ルール:
- SQL_IDのみ指定（例: `"CHECK_USER_EXISTS"`）→ マッピングするEntityクラスのパスから導出
  - `sample.entity.User` クラスの場合 → `sample/entity/User.sql`
- 別ファイルのSQLを使う場合は `#` で区切って指定（例: `"sample.entity.Member#CHECK_EXISTS"`）

SQLファイル記述例（`User.sql`）:
```sql
CHECK_USER_EXISTS=
SELECT
  USER_ID
FROM
  USERS
WHERE
  USER_ID = :userId
  AND STATUS = 'ACTIVE'
```

戻り値は `boolean` で、データが存在する場合 `true`、存在しない場合 `false` が返ります。

**注意点**:
- `exists` は内部で検索用SQLを変換して使用するため、SQLとしては通常の SELECT文を書けばよい（`COUNT(*)` などに書き換える必要はない）

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  任意のSQL(SQLファイル)で検索する
- class UniversalDao
  .claude/skills/nabledge-6/docs/javadoc/javadoc-nablarch-common-dao-UniversalDao.md
  exists