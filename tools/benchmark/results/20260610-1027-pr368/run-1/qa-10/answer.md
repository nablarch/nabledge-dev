**結論**: SQLファイルで `$if(プロパティ名) {SQL条件}` 構文を使用することで、対応するBeanプロパティがnullまたは空文字の場合にその条件を自動的にWHERE句から除外できる。

**根拠**:

SQLファイルで以下のように記述する。

```sql
-- SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    ...
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
    AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

条件を格納するBeanを作成し、UniversalDAOに渡す。

```java
// フォームの値を検索条件Beanにコピー
ProjectSearchDto searchCondition =
        BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// SQLファイルを指定して検索（searchConditionのnull/空プロパティに対応する条件は自動除外）
List<Project> result = UniversalDao
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

**`$if` の動作ルール:**
- `配列/Collection` の場合: プロパティ値がnullまたはサイズ0 → 条件除外
- それ以外の型の場合: プロパティ値がnullまたは空文字 → 条件除外

IN句で条件数が可変の場合は、名前付きパラメータの末尾に `[]` を付加する。

```sql
$if (userKbn) {user_kbn in (:userKbn[])}
```

**注意点**:
- `$if` が使えるのはwhere句のみ（ORDER BY句などには使用不可）
- `$if` の入れ子は不可
- 異なる機能でSQLを共通化する目的で使用しないこと。検索条件の共通化に安易に使うと変更時に思わぬ不具合を招く

参照: component/libraries/libraries-database.json:s21, component/libraries/libraries-database.json:s22, processing-pattern/web-application/web-application-getting-started-project-search.json:s1, component/libraries/libraries-universal-dao.json:s10