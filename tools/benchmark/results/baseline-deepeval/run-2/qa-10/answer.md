セクション選定が完了しました。s21（可変条件）が最重要セクションです。

**read_sections**: `libraries-database.json:s21`, `libraries-database.json:s16`, `libraries-database.json:s6`

---

## 回答生成

**結論**: SQLファイルに `$if(プロパティ名) {条件式}` 構文を使い、Beanのプロパティが null または空文字の場合に自動で条件を除外できます。`ParameterizedSqlPStatement` でBeanオブジェクトを渡すことで実現します。

**根拠**:

SQLファイルに可変条件を定義します：

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

`$if(プロパティ名)` の後のプロパティが以下の場合、その条件全体が除外されます：
- 文字列（String）の場合：null または空文字列
- 配列・Collection の場合：null またはサイズ0

Javaの実装は、Beanを `prepareParameterizedSqlStatementBySqlId` の第2引数に渡します：

```java
// 検索条件Beanを生成（入力がなかった項目はnullのまま）
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");  // userKbnは設定しない → 条件から除外される

AppDbConnection connection = DbConnectionContext.getConnection();

// 第2引数にBeanを渡すことで、$if条件の評価に使われる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

// entityのプロパティをバインド変数に設定してSQLを実行
SqlResultSet result = statement.retrieve(entity);
```

**注意点**:
- `$if` は where 句のみ使用可能です。`$if` のネスト（入れ子）はできません。
- この機能は「ユーザー入力によって条件が変わる検索画面」向けのものです。条件が異なるだけの複数SQLを共通化するためには使わないでください（変更時に意図しない不具合の原因になります）。
- like 検索と組み合わせる場合は、名前付きパラメータの末尾に `%` を付けます（例：`:userName%`）。

参照: `libraries-database.json:s21`

---