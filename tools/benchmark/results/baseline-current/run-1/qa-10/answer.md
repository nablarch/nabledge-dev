**結論**: SQLファイルに `$if(プロパティ名) {条件}` という特殊構文を使うことで、Beanオブジェクトのプロパティ値がnull・空の場合にその条件を自動的に除外できます。

**根拠**:

NablarchのデータベースアクセスライブラリはSQLファイル内で可変条件を記述する構文を提供しています。

**書き方**:

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

`$if(プロパティ名) {SQL条件}` の動作ルール:
- **String型**: プロパティ値が `null` または空文字の場合、その条件を除外
- **配列・Collection型**: プロパティ値が `null` またはサイズ0の場合、その条件を除外
- それ以外の型: プロパティ値が `null` の場合、除外

**Javaコード例**:

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");  // userKbn は未設定（null）

AppDbConnection connection = DbConnectionContext.getConnection();

ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
// → userKbn が null なので、user_kbn の条件は除外されて実行される
```

in句を可変にしたい場合は `$if` と `[]` を組み合わせます:

```sql
$if (userKbn) {user_kbn in (:userKbn[])}
```

**注意点**:
- `$if` が使えるのは **WHERE句のみ**（SELECT句・FROM句では使用不可）
- `$if` のネスト（`$if` の中に `$if`）は不可
- この機能は検索画面のようにユーザー入力によって条件が変わる場合を想定したもの。条件が異なるだけの複数SQLを1つに共通化する目的には使わないこと
- in句のプロパティ値がnull・サイズ0になりうる場合は、必ず `$if` との組み合わせで可変条件として定義すること（そうしないと `in (null)` になり検索結果が不正になる）

参照: `component/libraries/libraries-database.json#s21`, `component/libraries/libraries-database.json#s22`