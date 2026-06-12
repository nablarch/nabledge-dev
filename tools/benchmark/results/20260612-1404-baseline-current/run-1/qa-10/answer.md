**結論**: `$if(プロパティ名) {SQL文の条件}` という特殊構文をSQLファイルのwhere句に記述することで、Beanのプロパティ値がnull・空文字列の場合にその条件を自動的に除外できます。

**根拠**:

SQLファイルに `$if` 構文で可変条件を定義します。

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

Javaの実装では、`prepareParameterizedSqlStatementBySqlId` の**第2引数**に条件Beanを渡します。このBeanの状態を元にSQL文が動的に組み立てられます。

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");  // userKbnはnull（条件から除外される）

AppDbConnection connection = DbConnectionContext.getConnection();

// 2番目の引数に条件Beanを渡すことで可変条件が組み立てられる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

`$if` の除外条件：
- 配列・`java.util.Collection` → nullまたはサイズ0のとき除外
- それ以外（String等）→ nullまたは空文字列のとき除外

**in句が可変の場合**は、`$if` と `:パラメータ名[]` を組み合わせます：

```sql
select user_id, user_name, user_kbn
from user
where
  $if (userKbn) {user_kbn in (:userKbn[])}
```

```java
UserSearchCondition condition = new UserSearchCondition();
condition.setUserKbn(Arrays.asList("1", "3"));

ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", condition);

SqlResultSet result = statement.retrieve(condition);
```

**注意点**:
- `$if` はwhere句のみで使用可能。`$if` 内に `$if` はネストできません。
- `$if` は検索画面のように入力によって条件が変わる場合に使うもので、条件だけが異なる複数のSQLの共通化には使わないこと（共通化すると意図しない不具合の原因になります）。
- INパラメータにはJDBC標準の `?` ではなく、必ず名前付きパラメータ（`:プロパティ名`）を使うこと。

参照: libraries-database.json:s21, libraries-database.json:s22, libraries-database.json:s16