Step 4で必要なセクションの内容が揃いました。Step 5の回答を生成します。

---

**結論**: SQLファイルで `$if(プロパティ名) {条件}` 構文を使うことで、Beanのプロパティに値がある場合のみその条件をWHERE句に含める動的SQLが実現できます。

**根拠**:

SQLファイルに以下のように記述します。プロパティが null または空文字列の場合、その条件は自動的に除外されます。

```sql
-- Project.sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_START_DATE
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName)           {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectClass)          {PROJECT_CLASS IN (:projectClass[])}
```

Javaの実装は `UniversalDao.findAllBySqlFile` に検索条件Beanを渡すだけです。

```java
// 検索条件Beanを組み立て（値が入っている項目のみ条件に含まれる）
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

List<Project> result = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

検索条件Bean（`ProjectSearchDto`）のプロパティは、対応するカラムの型に合わせて定義します。

```java
public class ProjectSearchDto implements Serializable {
    private String projectName;                   // null or 空文字 → 条件から除外
    private java.sql.Date projectStartDateBegin;  // null → 条件から除外
    private List<String> projectClass;            // null or 空リスト → 条件から除外
    // getter/setter 省略
}
```

`$if` の除外判定ルール:
- `String` 型: null または空文字列のとき除外
- 配列・`Collection` 型: null またはサイズ0のとき除外
- それ以外: null のとき除外

**注意点**:
- `$if` は **WHERE句のみ**で使用可能で、`$if` のネストは不可
- この構文は検索条件が可変な場面専用。条件だけが異なる複数SQLの共通化には使わないこと（意図しない変更による不具合防止のため、SQLは機能ごとに定義する）
- IN句を可変にする場合はプロパティ名末尾に `[]` を付ける: `:projectClass[]`

参照: libraries-database.json:s21, libraries-universal-dao.json:s10, web-application-getting-started-project-search.json:s1

---