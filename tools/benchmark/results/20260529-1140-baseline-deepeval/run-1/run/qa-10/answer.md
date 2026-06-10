**結論**: SQLファイルに `$if(プロパティ名) {条件}` という特殊構文を使うことで、Beanのプロパティが null または空の場合にその条件を自動除外できます。`ParameterizedSqlPStatement` でBeanを渡して実行します。

**根拠**:

SQLファイルに以下のように記述します。

```sql
select
  user_id,
  user_name,
  user_kbn
from
  user
where
  $if (userName) {user_name like :userName%}
  and $if (userKbn) {user_kbn = :userKbn}
  and birthday = :birthday
```

- `$if (プロパティ名)` のプロパティが **null または空文字列** の場合、そのブロックがWHERE句から除外される
- プロパティが `Collection` や配列の場合は **null またはサイズ0** のときに除外される

Javaの実装は以下の通りです。

```java
// Beanに入力値を設定（userKbnは未入力のためnullのまま）
UserSearchCondition condition = new UserSearchCondition();
condition.setUserName("なまえ");
// condition.setUserKbn(null); // 設定しなければ除外される

AppDbConnection connection = DbConnectionContext.getConnection();

// 第2引数にBeanを渡して$if条件を評価させる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", condition);

// BeanのプロパティをバインドしてSQL実行
SqlResultSet result = statement.retrieve(condition);
```

IN句の条件数も可変にしたい場合は、`$if` と `[]` 記法を組み合わせます。

```sql
$if (userKbn) {user_kbn in (:userKbn[])}
```

**注意点**:
- `$if` が使えるのは **WHERE句のみ**（ORDER BY句などでは使用不可）
- `$if` のネストは不可
- この機能はウェブアプリの検索画面のように「ユーザ入力によって条件が変わる場合」を想定したもの。複数SQLを共通化するために使うものではなく、用途が異なるSQLは別々に定義すること

参照: libraries-database.json:s21, libraries-database.json:s22

---