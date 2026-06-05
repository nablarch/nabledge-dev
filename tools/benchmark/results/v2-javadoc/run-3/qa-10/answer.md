Step 4で読み込んだセクションを基に回答を生成します。

**結論**: SQLファイルに `$if(プロパティ名) {条件}` 構文を使用することで、対応するBeanプロパティが未入力（null/空文字）の場合に条件を自動的にWHERE句から除外できます。

**根拠**:

SQLファイルで可変条件を記述し、`prepareParameterizedSqlStatementBySqlId` の第2引数に条件BeanをわたすとSQL構築時に動的に組み立てられます。

```sql
-- SQLファイル例
SELECT_USERS =
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

この例では `userName` と `userKbn` が可変条件で、Beanプロパティが null または空文字列の場合、その条件はWHERE句から除外されます。

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ"); // userKbn は設定しない (null のまま)

AppDbConnection connection = DbConnectionContext.getConnection();

// 第2引数にBeanを渡す → SQLの可変条件が組み立てられる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#selectUsers", entity);

SqlResultSet result = statement.retrieve(entity);
// → user_kbn の条件は除外され、user_name like 'なまえ%' and birthday = ? のみが実行される
```

IN句の条件数を動的にしたい場合は、`$if` と `[]` 記法を組み合わせます。

```sql
$if (userKbnList) {user_kbn in (:userKbnList[])}
```

**注意点**:
- `$if` 構文はWHERE句内のみ使用可能
- `$if` のネストは不可
- in句のプロパティは配列か `java.util.Collection` 型で宣言すること。null またはサイズ0の場合は `$if` で可変条件にしないと `in (null)` となり意図しない結果になる
- この機能はウェブ検索画面のようにユーザー入力で条件が変わる場合向け。条件だけ異なる複数のSQLを共通化する目的では使用しないこと

参照: libraries-database.json:s21, libraries-database.json:s22

---