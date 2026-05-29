必要な情報が揃いました。回答を生成します。

---

**結論**: SQLファイルに `$if(プロパティ名) {SQL条件}` 構文を使って可変条件を記述し、Beanオブジェクトを入力としてSQLを実行することで、入力がある項目だけをWHERE条件に含められる。

**根拠**:

### `$if` 構文の書き方

SQLファイル内のWHERE句で以下の記法を使う：

```sql
$if(プロパティ名) {SQL文の条件}
```

条件が除外されるタイミング：
- `String` 型のプロパティ: `null` または空文字列のとき除外
- 配列・`Collection` 型: `null` またはサイズ0のとき除外

### SQLファイルの例（複数の可変条件）

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_TYPE,
    PROJECT_CLASS,
    PROJECT_START_DATE,
    PROJECT_END_DATE,
    VERSION
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(clientId)              {CLIENT_ID = :clientId}
    AND $if(projectName)           {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)           {PROJECT_TYPE = :projectType}
    AND $if(projectClass)          {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)   {PROJECT_START_DATE <= :projectStartDateEnd}
```

### Javaの実装例

```java
// フォームから検索条件Beanへ値をコピー
ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// UniversalDAOでSQLファイルを指定して検索
List<Project> results = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

`searchCondition` のプロパティが `null` または空文字列であれば、その `$if` ブロックはSQL実行時に自動的に除外される。

### 注意点

- `$if` 構文は **WHERE句のみ**で使用可能。`$if` のネストは不可。
- この機能は「同一画面で入力項目によって検索条件が変わる場合」のためのもの。**条件が異なる複数のSQLを1つに共通化する目的では使用しない**（保守性が低下し、変更時に不具合を埋め込むリスクがある）。
- SQLのバインド変数には必ず名前付きパラメータ（`:プロパティ名`）を使う。JDBC標準の `?` は動作しない。

参照: libraries-database.json:s21, web-application-getting-started-project-search.json:s1

---