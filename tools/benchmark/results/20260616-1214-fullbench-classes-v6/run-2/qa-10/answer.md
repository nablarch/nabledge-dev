**結論**: SQLファイルに `$if(プロパティ名) {SQL条件}` 構文で可変条件を定義し、条件Beanのプロパティが null または空文字の項目は実行時に自動的に条件から除外されます。

**根拠**:

SQL ファイル（可変条件の記法）

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

- `$if (プロパティ名) {条件}` と記述する。
- プロパティ値が **null または空文字列（String の場合）** のとき、その条件ブロックは SQL から除外される。
- 配列・`Collection` の場合は null またはサイズ 0 のとき除外。
- `$if` が使えるのは **where 句のみ**、かつ `$if` のネストは不可。

Javaの実装例

```java
// 入力がある項目だけセットする
UserEntity entity = new UserEntity();
entity.setUserName("なまえ"); // userKbn は設定しない（nullのまま）

AppDbConnection connection = DbConnectionContext.getConnection();

// 2番目の引数に条件Beanを渡すことで可変条件が組み立てられる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SearchAction#findUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

上記の場合、`userKbn` は null なので `user_kbn` の条件は除外され、`user_name like :userName%` と `birthday = :birthday` だけが実行される。

**注意点**:
- `$if` 内で IN 句を可変件数にしたい場合は `:param[]` 構文を組み合わせる（例: `$if (userKbn) {user_kbn in (:userKbn[])}`）。
- この機能はウェブアプリの検索画面のような「ユーザの入力によって条件が変わる」ケース専用。異なる SQL を共通化するために使うものではなく、条件が異なる SQL は必ず別々に定義すること。

参照: libraries-database.json:s21, libraries-database.json:s16, libraries-database.json:s22