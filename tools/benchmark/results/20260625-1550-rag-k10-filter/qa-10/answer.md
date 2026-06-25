### Answer

はい、`$if` 構文を使って実現できます。

**基本的な書き方**

SQLファイルの WHERE 句で `$if(プロパティ名) {条件式}` と記述します。Bean のプロパティ値が null または空文字（String の場合）のとき、その条件は自動的に除外されます。

```sql
SELECT user_id, user_name, user_kbn
FROM user
WHERE
  $if (userName) {user_name LIKE :userName%}
  AND $if (userKbn) {user_kbn = :userKbn}
  AND birthday = :birthday
```

**Java 側の実装**

```java
// 検索条件 Bean に値をセット（userKbn はセットしない → 条件から除外される）
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");

AppDbConnection connection = DbConnectionContext.getConnection();

// 2 番目の引数に Bean を渡す（$if の評価に使われる）
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**ウェブアプリケーションでの典型的な実装パターン**

フォーム → Bean のコピーは `BeanUtil` を使い、バリデーション後にそのまま渡します。

```java
@InjectForm(form = ProjectSearchForm.class, prefix = "searchForm", name = "searchForm")
public HttpResponse list(HttpRequest request, ExecutionContext context) {
    ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
    ProjectSearchDto searchCondition =
            BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

    List<Project> result = UniversalDao.findAllBySqlFile(
            Project.class, "SEARCH_PROJECT", searchCondition);
    // ...
}
```

**IN 句を可変条件にする場合**

複数選択条件は `$if` と `:プロパティ名[]` を組み合わせます。Bean のプロパティ型は配列か `java.util.Collection` にする必要があります。

```sql
AND $if (projectClass) {PROJECT_CLASS IN (:projectClass[])}
```

```java
condition.setProjectClass(Arrays.asList("1", "3"));
```

プロパティ値が null やサイズ 0 の場合、`$if` により条件ごと除外されます（IN 句は空にできないため、`$if` との併用が必須です）。

**注意点**

`$if` は WHERE 句でのみ使用可能で、`$if` 内に `$if` をネストすることはできません。また、この機能は「条件が変わる複数の SQL を共通化する」ためではなく、「ユーザー入力によって条件が変わる検索画面」向けのものです。条件だけが異なる SQL を安易に共通化すると、変更時に思わぬ不具合を招くため、SQL は複数定義することが推奨されています。