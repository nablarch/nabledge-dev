必要なセクションを取得しました。Step 5: 回答を生成します。

---

**Step 5 & 6 & 7: 回答生成・検証**

**結論**: SQLファイルに `$if(プロパティ名) {SQL条件}` 構文を使うことで、Beanのプロパティが `null` または空文字の場合に自動的にその条件を除外できます。

**検証**: 全Nablarch固有の記述（`$if`構文、`ParameterizedSqlPStatement`、`prepareParameterizedSqlStatementBySqlId`、`UniversalDao#findAllBySqlFile`）はセクション内容から直接サポートされています。

---

**結論**: SQLファイルの `$if(プロパティ名) {条件}` 構文を使い、BeanオブジェクトのプロパティがNullまたは空文字の場合にその条件を自動除外する。

**根拠**:

`$if` 構文の記述ルール — SQLファイルのWHERE句に記述する:

```sql
-- SQLファイルへの記述例 (Project.sql)
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_TYPE,
    PROJECT_START_DATE,
    PROJECT_END_DATE
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName)           {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)           {PROJECT_TYPE = :projectType}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)   {PROJECT_START_DATE <= :projectStartDateEnd}
```

除外される条件（プロパティ値が以下の場合に `$if` ブロックがSQL文から除かれる）:
- `String` の場合: `null` または空文字列
- 配列・`Collection` の場合: `null` またはサイズ0
- その他の型: `null`

**実装例1 — JDBCラッパー (`ParameterizedSqlPStatement`) で使う場合:**

```java
// 検索条件Beanに値を設定（未入力項目はnullのまま）
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");  // userKbnはnull → $if(userKbn) は除外される

AppDbConnection connection = DbConnectionContext.getConnection();

// Beanオブジェクトを渡すと、そのプロパティの状態でSQLを動的構築
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**実装例2 — UniversalDAO で使う場合（推奨）:**

```java
// フォームから検索条件Beanにコピー（BeanUtilで型変換も実施）
ProjectSearchDto searchCondition =
        BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// findAllBySqlFileの第2引数にSQLID、第3引数に条件Beanを渡す
List<Project> result = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

**in句の条件が可変な場合** — プロパティ名の末尾に `[]` を付加し、Beanのプロパティを配列または `Collection` 型にする:

```sql
AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
```

**注意点**:
- `$if` が使えるのはWHERE句のみ。`$if` の中に `$if` はネスト不可。
- `in` 句の条件でプロパティがnullになり得る場合は、必ず `$if` と組み合わせること（可変条件なしだと `IN (null)` になり検索結果が正しく取れない）。
- この構文はウェブ画面の検索条件のような「ユーザー入力によって変わる条件」向け。異なる複数SQLを共通化する目的には使わないこと（思わぬ不具合の原因になる）。

参照: `libraries-database.json:s21`, `libraries-database.json:s22`, `web-application-getting-started-project-search.json:s1`

---