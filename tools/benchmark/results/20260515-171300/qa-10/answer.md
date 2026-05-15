**結論**: `$if(プロパティ名) {SQL文の条件}` という特殊構文を使うことで、入力がある項目だけをWHERE句の条件に含めることができます。

**根拠**:

Nablarch の `ParameterizedSqlPStatement`（BeanオブジェクトでSQLを実行する機能）では、以下の構文で可変条件を記述します。

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

**除外ルール**（プロパティ値が以下の場合は条件がSQLから除外される）:
- 配列・`java.util.Collection` の場合: null またはサイズ0
- その他の型の場合: null または空文字列（String の場合）

Beanオブジェクトを `prepareParameterizedSqlStatementBySqlId` の第2引数に渡すと、Beanの状態に応じてSQLが動的に組み立てられます。

**制約**:
- `$if` が使えるのは **WHERE句のみ**
- `$if` の中に `$if` はネストできない
- IN句を可変にする場合は `:userKbn[]` のように末尾に `[]` を付加し、Beanのプロパティ型を配列または `Collection` にする必要がある

**注意点**:

この機能は「検索画面でユーザーの入力によって条件が変わる場合」に使うものです。条件だけが異なる複数のSQLを共通化する目的で使ってはいけません。安易に共通化すると、SQL変更時に予期しない不具合を埋め込む原因になるため、目的の異なるSQLは必ず別々に定義してください。

参照: `component/libraries/libraries-database.json#s21`, `component/libraries/libraries-database.json#s6`, `component/libraries/libraries-database.json#s22`