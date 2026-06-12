**結論**: UniversalDaoでデータベースを検索するには、SQLをファイルに外部化してSQL IDを指定し、`UniversalDao.findAllBySqlFile()` を呼び出します。検索条件がある場合は専用の条件Beanを第3引数に渡します。

---

**根拠**:

#### 1. 事前設定

コンポーネント定義に `BasicDaoContextFactory` を追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

#### 2. SQLファイルを作成する

SQLファイルのパスはBeanのクラス名から自動導出されます。`sample.entity.User` クラスなら `sample/entity/User.sql` となります。

```sql
FIND_BY_NAME =
SELECT
    USER_ID,
    USER_NAME
FROM
    USER
WHERE
    USER_NAME = :userName
```

動的条件には `$if` 構文を使います。

```sql
SEARCH_PROJECT =
SELECT * FROM PROJECT
WHERE
    $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(clientId) {CLIENT_ID = :clientId}
```

---

#### 3. 検索を実行する

**条件なし検索**:

```java
List<User> users = UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

**条件付き検索**（検索条件はEntityではなく専用のBeanを使用）:

```java
// 検索条件Beanにフォームの値をコピー（BeanUtilを使用）
ProjectSearchDto searchCondition =
        BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

List<Project> projects = UniversalDao.findAllBySqlFile(
        Project.class, "SEARCH_PROJECT", searchCondition);
```

検索条件Beanのプロパティ型は、対応するカラムの型と互換性のある型で定義します（例: `String` ではなく `java.sql.Date`）。

**ページング検索**:

```java
EntityList<Project> projects = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

// ページング情報の取得
Pagination pagination = projects.getPagination();
```

---

**注意点**:
- 検索条件Beanには、Entityではなく専用の条件Beanを使うこと（単一テーブルアクセスのみEntityでも可）
- 大量データを処理する場合はメモリ不足になるため、`UniversalDao.defer()` による遅延ロードを使用し、処理後に `DeferredEntityList#close()` を必ず呼び出すこと（try-with-resources 推奨）
- SQLはSQLインジェクション防止のため必ず外部ファイルに記述すること

参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s6, libraries-universal-dao.json:s9, web-application-getting-started-project-search.json:s1, restful-web-service-getting-started-search.json:s1

---