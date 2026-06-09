**結論**: `UniversalDao.findAllBySqlFile()`メソッドを使用してSQLファイルのSQL IDを指定してデータベースを検索します。条件を絞り込む場合は、検索条件Beanを第3引数に渡します。

**根拠**:

**1. 設定**

コンポーネント定義ファイルに `BasicDaoContextFactory` を追加します。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**2. 全件検索（SQLファイル使用）**

```java
// SQLファイル（User.sql）のSQL ID「FIND_BY_NAME」で検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは検索結果をマッピングするBeanクラスから自動的に導出されます（例: `sample.entity.User` → クラスパス配下の `sample/entity/User.sql`）。

**3. 条件を指定した検索**

```java
// 検索条件をBeanで渡す
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

SQLファイルでは、条件が入力された場合のみWHERE句に含める `$if` 構文が使えます。

```sql
SEARCH_PROJECT =
SELECT PROJECT_ID, PROJECT_NAME
FROM PROJECT
WHERE
    $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
```

**4. ページングを伴う検索**

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

**5. 大量データの遅延ロード**

```java
// try-with-resourcesを使ったclose呼び出し
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**注意点**:
- 検索条件Beanのプロパティは、対応するカラムの型と互換性のある型で定義すること
- 遅延ロード（`defer()`）使用時は必ず `DeferredEntityList#close()` を呼び出すこと。closeしないとサーバサイドカーソルのリソースリークが発生する
- `UniversalDao` は主キー以外の条件を指定した更新/削除には対応していない（その場合はデータベースアクセス(JDBCラッパー)を使用する）

参照: libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, web-application-getting-started-project-search.json:s1