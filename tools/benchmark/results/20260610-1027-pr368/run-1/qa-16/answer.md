**結論**: `UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` を呼び出す。SQL_IDで指定したSQLを使ってデータの存在チェックを行い、存在すれば `true` を返す。

**根拠**:

**シグネチャ**:

```java
// バインド変数なし
public static boolean exists(Class<T> entityClass, String sqlId)

// バインド変数あり
public static boolean exists(Class<T> entityClass, String sqlId, Object params)
```

**実装例（バインド変数あり）**:

```java
// 検索条件をBeanに設定する
User condition = new User();
condition.setUserId(123L);

boolean exists = UniversalDao.exists(User.class, "FIND_BY_ID", condition);
```

**SQLファイルの配置**:

SQLファイルのパスは第1引数のエンティティクラスから自動導出される。例えば `sample.entity.User` の場合、クラスパス配下の `sample/entity/User.sql` が使用される。

```sql
FIND_BY_ID =
select
  1
from
  users
where
  user_id = :userId
```

**別のSQLファイルを指定する場合（`#` 区切り）**:

```java
// sample/entity/User.sql の FIND_BY_ID を使用
boolean exists = UniversalDao.exists(GoldUser.class, "sample.entity.User#FIND_BY_ID", condition);
```

`#` を含めると「SQLファイルパス#SQLID」と解釈される。基本は `#` なしの指定を使用し、機能単位にSQLを集約したい場合に限って使う。

内部では検索用のSQLを変換して存在チェックに使用する（`exists` 専用の変換処理が行われる）。

**注意点**:
- `exists` を使うには、`findAllBySqlFile` 等と同様に `BasicDaoContextFactory` のコンポーネント定義が必要。
- SQLファイルは機能ごとに作成し、複数機能で流用しないこと。

参照: `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17`, `javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18`, `component/libraries/libraries-universal-dao.json:s7`, `component/libraries/libraries-database.json:s12`