**結論**: UniversalDaoでページングを実装するには、`UniversalDao.per(件数).page(ページ番号)` を検索前に呼び出し、`findAllBySqlFile` で検索を実行します。

**根拠**:

**基本的なページング実装**:

`UniversalDao#per` と `UniversalDao#page` を検索前に呼び出すことでページングを実行できます。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

- `per(3)`: 1ページあたり3件
- `page(1)`: 1ページ目を取得

**ページング情報の取得**:

検索結果の `EntityList` から `Pagination` オブジェクトを取得できます。

```java
Pagination pagination = users.getPagination();
```

**SQLファイルを使った検索条件付きページング**:

検索条件がある場合は、専用のBean（Entityではなく）を条件として渡します。

```java
ProjectSearchForm condition = context.getRequestScopedVar("form");
List<Project> projects = UniversalDao.per(10).page(pageNum)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", condition);
```

**低レベルAPIでのページング（参考）**:

JDBCラッパーを直接使う場合は `SelectOption` で範囲を指定します。

```java
AppDbConnection connection = DbConnectionContext.getConnection();
SqlPStatement statement = connection.prepareStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#findUser", new SelectOption(11, 10));
SqlResultSet result = statement.retrieve();
```
（この例では11件目から最大10件を取得）

**注意点**:

- ページング処理では、範囲指定レコード取得の前に**件数取得SQL**が先に発行されます。元SQLが `ORDER BY` 句を含む場合、件数取得時に不要な処理負荷が発生する場合があります。
- 性能劣化が問題になる場合は、Dialectをカスタマイズして `convertCountSql` の実装を変更することで件数取得SQLをカスタマイズできます。
- 検索条件には専用Bean（Entityではなく）を使用してください。ただし、単一テーブルアクセスの場合はEntityも可です。
- `SelectOption` を使った低レベルAPIは UniversalDao より下位レイヤーです。通常は UniversalDao の `per/page` を使用してください。

参照: `libraries-universal_dao.json#paging`, `libraries-universal_dao.json#extension-examples`, `libraries-universal_dao.json#conditional-search`, `libraries-universal_dao.json#sql-file-search`, `libraries-database.json#execute-sql-with-range`
