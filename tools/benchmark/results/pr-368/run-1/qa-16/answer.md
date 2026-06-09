**結論**: `UniversalDao.exists(entityClass, sqlId)` または `UniversalDao.exists(entityClass, sqlId, params)` を呼び出すことで、SQL_IDを指定してデータ存在チェックができる。いずれもデータが存在すれば `true` を返す。

**根拠**:

バインド変数なし版（`exists(Class, String)`）:
```java
public static boolean exists(Class<T> entityClass, String sqlId)
```
SQL_IDをもとに検索し、データが存在するか否かを確認する。

バインド変数あり版（`exists(Class, String, Object)`）:
```java
public static boolean exists(Class<T> entityClass, String sqlId, Object params)
```
SQL_IDをもとにバインド変数を展開して検索し、データが存在するか否かを確認する。

**SQL_IDの指定形式**:

SQL_IDに `#` が含まれると、`SQLファイルのパス#SQL ID` と解釈する。

```java
// #なし: entityClassのFQCNからSQLファイルパスを導出
// User.classがsample.entity.Userなら → sample/entity/User.sql の CHECK_USER_EXISTS を使用
boolean exists = UniversalDao.exists(User.class, "CHECK_USER_EXISTS");

// #あり: 明示的にSQLファイルのパスを指定
// → sample/entity/Member.sql の CHECK_USER_EXISTS を使用
boolean exists = UniversalDao.exists(GoldUser.class, "sample.entity.Member#CHECK_USER_EXISTS");
```

バインド変数が必要な場合は、条件Beanを渡す:
```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して存在チェックする
boolean exists = UniversalDao.exists(Project.class, "CHECK_PROJECT", condition);
```

**SQLファイルの作成**（クラスパス配下に配置）:
```sql
-- データ存在確認SQL
CHECK_USER_EXISTS =
select
   1
from
   user_table
where
   user_id = :userId
```

**前提設定**: `BasicDaoContextFactory` をコンポーネント定義に追加する。
```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- 検索条件はEntityではなく専用Beanを指定することが推奨される（1テーブルのみへのアクセスの場合はEntityを指定してもよい）。
- `#` を含めた指定は機能単位にSQLを集約したい場合に使用できるが、指定が煩雑になるため基本は `#` なしの指定を使用すること。

参照: javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s17, javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s18, component/libraries/libraries-universal-dao.json:s7, component/libraries/libraries-universal-dao.json:s6, component/libraries/libraries-universal-dao.json:s10, component/libraries/libraries-database.json:s12