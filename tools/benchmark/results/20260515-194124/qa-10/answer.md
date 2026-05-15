**結論**: `$if(プロパティ名) {SQL条件}` という特殊構文を使うことで、入力がある項目だけをWHERE句の条件に含めることができます。

**根拠**:

NablarchのJDBCラッパー（`ParameterizedSqlPStatement`）は、Beanオブジェクトの状態を元にSQLを動的に構築する機能を提供しています。

**可変条件の記述ルール**

SQLファイルで `$if(プロパティ名) {条件式}` と記述します。Beanオブジェクトの対応プロパティが以下の値のとき、その条件は自動的に除外されます。

- 配列・`java.util.Collection` → nullまたはサイズ0
- その他の型 → nullまたは空文字列（Stringの場合）

**SQL記述例**

```sql
select
  user_id,
  user_name,
  user_kbn
from
  user
where
  $if (userName) {user_name like :userName%}
  and $if (userKbn) {user_kbn in ('1', '2')}
  and birthday = :birthday
```

`userName` のみ値がセットされた場合、`user_kbn` の条件は実行時に除外されます。

**Java実装例**

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");  // userKbn は null のまま

AppDbConnection connection = DbConnectionContext.getConnection();

ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**IN句も可変にする場合**

IN句の条件数も可変にしたい場合は、パラメータ末尾に `[]` を付け、`$if` と組み合わせます。

```sql
where
  $if (userKbn) {user_kbn in (:userKbn[])}
```

Beanのプロパティ型は配列または `java.util.Collection` にする必要があります。

**注意点**:
- `$if` が使えるのは **WHERE句のみ**（ORDER BY句の動的切り替えは `$sort` を使う）
- `$if` のネストは不可
- 条件だけが異なる複数SQLの安易な共通化目的での使用は非推奨（不具合の原因になるため、そのような場合はSQLを複数定義すること）

参照: `component/libraries/libraries-database.json#s21`, `component/libraries/libraries-database.json#s22`, `component/libraries/libraries-database.json#s6`