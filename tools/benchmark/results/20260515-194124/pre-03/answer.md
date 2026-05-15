**結論**: UniversalDaoでのデータベース検索は、主に3つの方法があります。①主キー指定による単純検索、②SQLファイルを使った任意条件検索、③条件Beanを使った動的検索です。

**根拠**:

### 1. 主キーを指定した検索（SQL不要）

`@Entity` などのJakarta PersistenceアノテーションをEntityに付けるだけで、SQLを書かずに主キー検索ができます（`UniversalDao`のメソッドを使用）。

### 2. 任意のSQL（SQLファイル）で検索する

SQLファイルを作成し、SQL IDを指定して検索します。

```java
// 全件検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");

// 別クラスのSQLファイルを指定する場合（#で区切る）
UniversalDao.findAllBySqlFile(GoldUser.class, "sample.entity.Member#FIND_BY_NAME");
```

SQLファイルのパスは、マッピング先BeanのクラスパスFQCNから導出されます。例: `sample.entity.User` → `クラスパス配下/sample/entity/User.sql`

### 3. 条件を指定して検索する

検索フォームなどの条件Beanを第3引数に渡すことで、WHERE句の条件を動的に指定できます。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件はEntityではなく専用のBeanを指定すること（単一テーブルのみの場合はEntityでも可）。

### 4. ページング検索

`per(件数).page(ページ番号)` を先に呼び出します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

### 5. 大量データの遅延ロード

大量データを扱う場合は `defer()` を先に呼び出し、`DeferredEntityList` を `try-with-resources` で使用します。

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
- 検索結果をマッピングするBeanのプロパティ名とSELECT句のカラム名が一致する必要があります
- 主キー以外の条件を指定した更新/削除はUniversalDaoでは行えないため、データベースアクセス（JDBCラッパー）を使用してください
- 遅延ロード中にトランザクション制御を行うとカーソルがクローズされる場合があるため注意が必要です
- 悲観的ロック（SELECT FOR UPDATE）が必要な場合は `UniversalDao#findBySqlFile` でSQLに行ロックを記述してください

参照: `libraries-universal-dao.json#s2`, `libraries-universal-dao.json#s3`, `libraries-universal-dao.json#s7`, `libraries-universal-dao.json#s9`, `libraries-universal-dao.json#s10`, `libraries-universal-dao.json#s12`