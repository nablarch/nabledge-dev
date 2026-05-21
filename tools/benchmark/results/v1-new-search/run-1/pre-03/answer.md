セクションの内容を確認しました。回答を生成します。

---

**結論**: `UniversalDao.findAllBySqlFile` メソッドにSQLファイルのIDと検索条件Beanを渡すことで、検索結果をBeanのリストとして取得できます。

**根拠**:

**1. 基本的な検索（SQLファイル使用）**

SQLファイルを作成し、SQL IDを指定して検索します。検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目へ自動マッピングされます。

```java
// 全件検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、マッピング先のBeanクラスから自動導出されます（例: `sample.entity.User` → `sample/entity/User.sql`）。

**2. 条件を指定した検索**

検索条件Beanを第3引数に渡します。BeanのプロパティがSQL内のバインド変数に対応します。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

```sql
-- SQL例（$if構文で任意条件を記述）
SEARCH_PROJECT =
SELECT PROJECT_ID, PROJECT_NAME FROM PROJECT
WHERE
  $if(projectName) {PROJECT_NAME LIKE :%projectName%}
  AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

> 検索条件はEntityではなく専用の条件Beanを使用してください（1テーブルのみへのアクセスの場合はEntityも可）。

**3. ページング**

```java
EntityList<Project> projects = UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

// ページング情報の取得
Pagination pagination = projects.getPagination();
```

**4. 大量データの遅延ロード**

大量データを扱う場合は `defer()` を使用します。`DeferredEntityList` は必ず `close` してください。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**注意点**:
- ユニバーサルDAOを使用するには、JDBCラッパーの設定に加えて `BasicDaoContextFactory` のコンポーネント定義が必要です。
- 遅延ロード使用中はトランザクション制御でカーソルがクローズされる場合があります（DBベンダーのマニュアルを確認してください）。
- 主キー以外の条件を使った更新・削除はユニバーサルDAOでは行えないため、JDBCラッパーを使用してください。

参照: libraries-universal-dao.json:s3, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, libraries-universal-dao.json:s6, web-application-getting-started-project-search.json:s1

---