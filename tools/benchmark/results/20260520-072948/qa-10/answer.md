**結論**: ウェブアプリケーションの検索画面で動的SQLを実装するには、SQLファイルの `$if(プロパティ名) {条件}` 構文を使い、Beanのプロパティが null または空文字の場合に自動的にその条件を除外できる。

**根拠**:

`$if` を使った可変条件のSQL例（`user_name` と `user_kbn` が入力された場合のみ条件に含まれる）:

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

実装例（`userName` のみ入力されている場合、`user_kbn` 条件は自動除外される）:

```java
// 検索条件Beanを生成
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");
// userKbn は未設定のまま（null）→ user_kbn 条件は除外される

AppDbConnection connection = DbConnectionContext.getConnection();

// 2番目の引数にBeanを渡してSQL組み立てを行う
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**除外される条件のルール**:
- `String` 型: 値が `null` または空文字列の場合に除外
- 配列・`Collection` 型: 値が `null` またはサイズ0の場合に除外

**注意点**:
- `$if` が使えるのは `where` 句のみ。`$if` のネストは不可。
- in句の項目数が可変になる場合は `:プロパティ名[]` の記法と `$if` を組み合わせる:

```sql
where
  $if (userKbn) {user_kbn in (:userKbn[])}
```

- この機能はユーザー入力による条件変化を扱うもの。複数の異なるSQLの共通化目的での使用は不可（SQLを個別に定義すること）。

参照: component/libraries/libraries-database.json:s21, component/libraries/libraries-database.json:s22