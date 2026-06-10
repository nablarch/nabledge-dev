**結論**: UniversalDaoでデータベースを検索するには、SQLファイルを作成してSQL IDを指定し、`UniversalDao.findAllBySqlFile`（複数件）または`UniversalDao.findBySqlFile`（1件）を呼び出します。

---

**根拠**:

#### 1. 事前設定

コンポーネント定義に`BasicDaoContextFactory`を追加する必要があります。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

#### 2. 基本的な検索（全件 / 条件付き）

SQLファイルを作成し、SQL IDを指定して`findAllBySqlFile`を呼び出します。

```java
// 全件検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");

// 条件を指定して検索（条件は専用のBeanで渡す）
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

SQLファイルは検索結果をマッピングするBeanのクラスパスから導出されます。例えば`sample.entity.User`の場合、`sample/entity/User.sql`に配置します。

SQLファイルの例（`$if`構文で動的条件を構築）:

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_START_DATE
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

#### 3. 1件検索

```java
// 対象が存在しない場合はNoDataExceptionを送出する
ProjectDto dto = UniversalDao.findBySqlFile(
    ProjectDto.class, "FIND_BY_PROJECT",
    new Object[]{targetForm.getProjectId(), userContext.getUserId()});
```

#### 4. ページング検索

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

Webアプリでの実装例:

```java
return UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

#### 5. 大量データの遅延ロード検索

```java
// try-with-resourcesでcloseを確実に呼ぶ
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

Jakarta Batchでの遅延ロード例（`ItemReader`の`open`メソッド内）:

```java
list = (DeferredEntityList<EmployeeForm>) UniversalDao.defer()
        .findAllBySqlFile(EmployeeForm.class, "SELECT_EMPLOYEE");
iterator = list.iterator();
```

---

**注意点**:
- 条件を指定して検索する場合、検索条件はEntityではなく**専用のBean**（検索条件Bean）を使用すること（単一テーブルのみアクセスする場合はEntityを指定しても可）
- 遅延ロード（`defer()`）使用時は、内部でサーバサイドカーソルを使用するため、**`DeferredEntityList#close`を必ず呼び出す**こと。呼び出さないとリソースリークが発生する
- RDBMSによっては、遅延ロード中にトランザクション制御を行うとカーソルがクローズされエラーになる場合がある。大量データ処理でトランザクション制御が必要な場合はページングで回避すること

参照: libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s9, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, web-application-getting-started-project-search.json:s1, web-application-getting-started-project-update.json:s1, jakarta-batch-getting-started-chunk.json:s2