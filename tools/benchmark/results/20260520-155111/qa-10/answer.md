**結論**: `$if(プロパティ名) {SQL文の条件}` 構文をSQLファイルに記述することで、Beanのプロパティ値がnull・空文字の場合にその条件を自動的に除外できる。

**根拠**:

SQLファイルに `$if` 構文で可変条件を記述する。

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

Javaコード側では `ParameterizedSqlPStatement` を使用し、Beanオブジェクトを渡す。

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");  // userKbn は未設定(null)

AppDbConnection connection = DbConnectionContext.getConnection();
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#insertUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

上記の場合、`userKbn` がnullのため `user_kbn in ('1', '2')` 条件は除外されて実行される。

**条件が除外されるルール**:
- 配列・`java.util.Collection` の場合: プロパティ値が null またはサイズ0
- その他の型の場合: プロパティ値が null または空文字列（String の場合）

**in句の件数も可変にする場合**は `:プロパティ名[]` を使用する。

```sql
select user_id, user_name, user_kbn
from user
where
  $if (userKbn) {user_kbn in (:userKbn[])}
```

```java
condition.setUserKbn(Arrays.asList("1", "3"));
// → 実行SQL: user_kbn in (?, ?) となる
```

**注意点**:
- `$if` が使用できるのは WHERE 句のみ（他の句では使用不可）
- `$if` の入れ子は不可
- この機能はウェブアプリケーションの検索画面での条件切り替え向け。条件だけ異なる複数SQLを共通化する用途には使わないこと（安易な共通化は不具合の原因になる）

参照: libraries-database.json:s21, libraries-database.json:s22