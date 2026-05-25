**結論**: `$if(プロパティ名) {SQL文の条件}` 構文を使うことで、入力がある項目だけをWHERE句の条件に含める動的SQLを記述できます。

**根拠**:

`ParameterizedSqlPStatement` を使い、SQL内で `$if` 構文を記述します。指定したBeanプロパティが `null`・空文字・空コレクションの場合、その条件は自動的に除外されます。

**SQL例**（`userName` と `userKbn` が可変条件）:
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

**実装例**（`userName` のみ設定 → `userKbn` の条件は除外される）:
```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");

AppDbConnection connection = DbConnectionContext.getConnection();
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

IN句の条件数も可変にしたい場合は、名前付きパラメータの末尾に `[]` を付けてBeanのプロパティを配列または `Collection` にします:
```sql
$if (userKbn) {user_kbn in (:userKbn[])}
```

**注意点**:
- `$if` が使えるのは **WHERE句のみ**。`$if` のネストは不可
- この機能は「ユーザ入力によって条件が変わる検索画面」向けの機能。条件だけ異なる複数SQLの共通化に使うものではない
- IN句でプロパティ値が `null` やサイズ0になる可能性がある場合は、必ず `$if` と組み合わせること（そうしないと `in (null)` になり結果が正しく取れない）
- Beanのプロパティは内部で `BeanUtil` を使ってMapに変換されるため、`BeanUtil` 非対応の型は使用不可

参照: `knowledge/component/libraries/libraries-database.json#s21`, `knowledge/component/libraries/libraries-database.json#s22`, `knowledge/component/libraries/libraries-database.json#s6`