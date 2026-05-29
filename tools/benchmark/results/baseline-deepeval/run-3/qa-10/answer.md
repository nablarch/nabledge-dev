十分な情報が集まりました。Step 5で回答を生成します。

---

**結論**: `$if(プロパティ名) {SQL条件}` 構文を使ってSQLファイルに可変条件を記述することで、入力がある項目だけを検索条件に含めることができます。

**根拠**:

**SQLファイルへの記述方法：**

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

`$if(プロパティ名) {SQL条件}` の動作ルール：

- プロパティ値が **null または空文字列（String型の場合）** のとき → その条件が除外される
- プロパティ値が **配列または `Collection` でサイズ0またはnull** のとき → 除外される
- それ以外（値が設定されている）のとき → 条件が有効になる

**in句の可変条件：** IN句を使う場合はプロパティ名の末尾に `[]` を付けます。

```sql
AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
```

**Javaアクション側の実装：**

```java
// 検索条件Beanを生成（フォームの値をコピー）
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// UniversalDAOでSQLIDを指定して実行
return UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

フォーム → 検索条件Beanへの値コピーは `BeanUtil.createAndCopy()` を使います。

**注意点**:

- `$if` が使えるのは **where句のみ**（order by等には使えない）
- `$if` の中に `$if` はネストできない
- 複数機能でSQLを流用せず、機能ごとに別々のSQLを定義すること（Nablarchの推奨）

参照: `component/libraries/libraries-database.json:s21`, `component/libraries/libraries-database.json:s22`, `processing-pattern/web-application/web-application-getting-started-project-search.json:s1`

---