**結論**: SQLファイルで `$if` 特殊構文を使用することで、Beanのプロパティに値がある項目のみをWHERE条件に含める可変条件SQLを実装できます。

**根拠**:

**SQLの記述方法**

`$if(プロパティ名) {SQL文の条件}` の形式で可変条件を記述します。プロパティ値が null または空文字（String型）の場合、その条件はSQLから除外されます。配列・`java.util.Collection` の場合は null またはサイズ0で除外されます。

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

この例では `userName` と `userKbn` が可変条件です。`userName` のみに値が設定されている場合、`user_kbn` の条件は実行時に除外されます。

**Javaの実装**

条件Beanをステートメント生成時（第2引数）と実行時（`retrieve` メソッド引数）の両方に渡します。

```java
// beanを生成しプロパティに値を設定
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");
// userKbnは設定しない → 条件から除外される

// DbConnectionContextからデータベース接続を取得する
AppDbConnection connection = DbConnectionContext.getConnection();

// SQLIDを元にステートメントを生成する
// 2番目の引数に条件Beanを渡すことでSQL動的構築が行われる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#insertUser", entity);

// entityのプロパティの値をバインド変数に設定しSQLが実行される
SqlResultSet result = statement.retrieve(entity);
```

**ユニバーサルDAOを使う場合**

ユニバーサルDAOでも同じSQLファイル機構を使用するため、`findAllBySqlFile` に検索条件Beanを渡すことで同様の可変条件SQLが実行できます。

```java
ProjectSearchForm condition = context.getRequestScopedVar("form");

List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

**注意点**:
- `$if` はwhere句のみ使用可能です（order by句などには使用不可）
- `$if` 内に `$if` をネストして使用することはできません
- この機能はウェブアプリケーションの検索画面のようにユーザー入力により条件が変わる場合に使用するものです。複数のSQLを共通化する目的での使用は避けてください（意図しない不具合の原因になります）

参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  可変条件を持つSQLを実行する
  Beanオブジェクトを入力としてSQLを実行する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  条件を指定して検索する