**結論**: JDBCラッパーの `$if` 構文を使い、SQLファイルに可変条件を記述する。Beanプロパティがnull/空文字列の場合にその条件が自動的に除外される。

**根拠**:

SQLファイルに以下の記法で可変条件を定義する。

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_TYPE,
    PROJECT_CLASS,
    PROJECT_START_DATE
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
    AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

`$if (プロパティ名) {SQL条件}` の意味:
- 対応するBeanプロパティが **null** または **空文字列**（String型の場合）→ 条件除外
- 配列・Collectionの場合は **null** または **サイズ0** → 条件除外
- それ以外（値あり）→ 条件に含める

実装側では、Beanを条件として `prepareParameterizedSqlStatementBySqlId` の第二引数に渡す。

```java
// beanを生成しプロパティに値を設定（入力のなかった項目はnullのまま）
UserSearchCondition condition = new UserSearchCondition();
condition.setUserName("なまえ"); // このプロパティのみ値あり

AppDbConnection connection = DbConnectionContext.getConnection();

// 第二引数にBeanを渡すことでSQLの可変条件が組み立てられる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", condition);

SqlResultSet result = statement.retrieve(condition);
```

ユニバーサルDAOで検索する場合も同様のSQL（SQLIDで指定）が使える。

```java
return UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

in句を可変にする場合は `:プロパティ名[]` と `$if` を組み合わせる。

```sql
AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
```

Beanの該当プロパティは配列か `java.util.Collection` 型で定義する。

**注意点**:
- `$if` 構文は **where句のみ** で使用可能。`$if` 内に `$if` をネストできない。
- この機能は検索画面のような「ユーザ入力内容によって条件が変わる」用途向け。条件だけが異なる複数のSQLを1つに共通化する目的での使用は推奨されない（変更時に意図しない影響が発生するリスクがある）。

参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  実行時のBeanオブジェクトの状態を元にSQL文を動的に構築できる
  可変条件を持つSQLを実行する
  in句の条件数が可変となるSQLを実行する
- 検索機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md
  検索する