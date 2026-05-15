**結論**: `$if` 特殊構文を使って、Beanのプロパティ値がnullまたは空文字の場合に WHERE 句の条件を自動的に除外できます。

**根拠**:

Nablarchのデータベースアクセス(JDBCラッパー)には「可変条件」機能があり、SQLファイル内で `$if` 構文を使って入力がある項目だけ条件に含める動的SQLを記述できます。

**SQLファイル例**:
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

**実装例**:
```java
// 条件Beanを生成（userNameのみ設定、userKbnはnull）
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");
// userKbn は設定しないので、user_kbn の条件は除外される

AppDbConnection connection = DbConnectionContext.getConnection();

// 2番目の引数に条件Beanを指定して $if の評価を行う
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**除外の判定ルール**:

| プロパティの型 | 除外される条件 |
|---|---|
| 配列 / `java.util.Collection` | null またはサイズ0の場合 |
| String | null または空文字列の場合 |
| その他 | null の場合 |

**in句を動的にしたい場合**は `$if` と `[]` を組み合わせます：
```sql
where
  $if (userKbn) {user_kbn in (:userKbn[])}
```

**注意点**:
- `$if` が使用できるのは **WHERE句のみ**。SELECT句やORDER BY句には使用不可
- `$if` の中に `$if` をネストすることは**不可**
- この機能は「ユーザー入力によって検索条件が変わる」用途向け。異なる複数SQLを共通化するために使うと保守性が下がるため、目的ごとにSQLを個別定義すること
- SQLはSQLファイルで管理し、`ParameterizedSqlPStatement` を使って実行する

参照: `libraries-database.json#s21`（可変条件を持つSQLを実行する）、`libraries-database.json#s22`（in句の条件数が可変となるSQLを実行する）