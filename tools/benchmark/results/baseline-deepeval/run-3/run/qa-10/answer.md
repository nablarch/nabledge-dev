**結論**: SQLファイルに `$if(プロパティ名) {条件}` 構文で可変条件を記述し、`ParameterizedSqlPStatement` で実行する。入力がない項目（null または空文字）の条件は自動的に除外される。

**根拠**:

SQLファイルに `$if` を使って可変条件を記述する。

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

Javaの実装では、`prepareParameterizedSqlStatementBySqlId` の **第2引数に条件 Bean を渡す**ことで可変条件が組み立てられる。

```java
// 検索条件 Bean に入力値を設定（userKbn は未入力なのでセットしない）
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");

AppDbConnection connection = DbConnectionContext.getConnection();

// 第2引数に Bean を渡して可変条件を構築する
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

// Bean の値をバインド変数に設定して実行
SqlResultSet result = statement.retrieve(entity);
```

`userName` にのみ値が設定されているため、`user_kbn` の条件は実行時に除外される。

**除外判定ルール**:
- `String` 型 → null または空文字の場合に除外
- 配列・`Collection` 型 → null またはサイズ0の場合に除外

**注意点**:
- `$if` が使用できるのは **where 句のみ**（order by などには使用不可）
- `$if` の入れ子は不可
- in句の条件数も可変にしたい場合は `$if (userKbn) {user_kbn in (:userKbn[])}` のように `:プロパティ名[]` 記法と組み合わせる（Bean のプロパティ型は配列または `Collection`）
- この機能は検索画面のように条件が変わるユースケース向け。複数 SQL の共通化に安易に使用しないこと

参照: libraries-database.json:s21, libraries-database.json:s22

---