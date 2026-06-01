**結論**: `$if(プロパティ名) {SQL条件}` 構文をSQLファイルに記述することで、Beanのプロパティが null または空文字の場合にその条件を自動的に除外できます。

**根拠**:

**SQLファイルでの記述方法**

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
    AND $if(clientId)               {CLIENT_ID = :clientId}
    AND $if(projectName)            {PROJECT_NAME LIKE  :%projectName%}
    AND $if(projectType)            {PROJECT_TYPE = :projectType}
    AND $if(projectClass)           {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin)  {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)    {PROJECT_START_DATE <= :projectStartDateEnd}
$sort(sortId){
    (idAsc PROJECT_ID)
    (nameAsc PROJECT_NAME, PROJECT_ID)
}
```

プロパティが null または空文字（String型）の場合、その `$if` ブロックがWHERE句から除外されます。配列・`Collection` の場合は null またはサイズ0のときに除外されます。

**検索条件Beanの作成**

フォームの値をBeanUtilで検索条件Beanにコピーして渡します。

```java
ProjectSearchDto searchCondition =
    BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);
```

**UniversalDaoで実行**

```java
return UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

`findAllBySqlFile` の第2引数にSQLID（例: `"SEARCH_PROJECT"`）、第3引数に検索条件Beanを渡します。

**注意点**:
- `$if` 構文はWHERE句のみで使用可能。`$if` のネストは不可。
- この機能は**検索画面のように入力内容によって条件が変わる場合**に使用するもの。条件だけが異なる複数SQLを共通化する目的での使用は不可（SQL変更時に思わぬ不具合の原因になる）。
- in句の条件が可変になる場合は `:projectClass[]` のように末尾に `[]` を付ける。可変条件でない場合にプロパティがnullだと `in (null)` となり検索結果が正しく取れないため、**in句は必ず `$if` と組み合わせる**こと。

参照: libraries-database.json:s21, web-application-getting-started-project-search.json:s1, libraries-database.json:s22, libraries-universal-dao.json:s10

---