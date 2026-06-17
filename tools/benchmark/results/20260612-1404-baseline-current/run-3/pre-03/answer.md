**結論**: UniversalDaoでDBデータを検索するには、`UniversalDao.findById`（主キー1件）・`UniversalDao.findAll`（全件）・`UniversalDao.findAllBySqlFile` / `UniversalDao.findBySqlFile`（任意SQL複数件/1件）を目的に合わせて使います。

**根拠**:

#### 1. 主キーで1件取得

```java
// 該当なしの場合は NoDataException が発生する
User user = UniversalDao.findById(User.class, userId);

// 該当なしの場合は null を返したい場合
User user = UniversalDao.findByIdOrNull(User.class, userId);
```

#### 2. 全件取得

```java
EntityList<User> users = UniversalDao.findAll(User.class);
```

#### 3. 条件を指定して複数件取得（SQLファイル）

SQLファイル（例: `sample/entity/Project.sql`）に `SEARCH_PROJECT` というSQL IDを定義し、条件BeanをBindします。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件は専用のBeanを使うこと。1テーブルのみへのアクセスの場合はEntityを指定しても良い。

#### 4. 条件を指定して1件取得

```java
Book condition = new Book();
condition.setId(1L);

Book book = UniversalDao.findBySqlFile(Book.class, "FIND_BY_ID", condition);
```

#### 5. ページングを行う場合

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

#### 6. 大量データの遅延ロード

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

> `DeferredEntityList#close` の呼び出しが必要なため、try-with-resourcesを使うこと。

**注意点**:
- `findAllBySqlFile` のSQLファイルのパスは、検索結果をマッピングするBeanのFQCNから自動導出される（例: `sample.entity.User` → クラスパス配下の `sample/entity/User.sql`）
- 遅延ロード（`defer`）使用中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされてエラーになる場合があるので注意
- `findBySqlFile` で複数件ヒットする場合は例外を送出せず先頭行を返却するため、1件であることが保証されるSQL条件を設定すること

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s7, libraries-universal-dao.json:s9, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, javadoc-nablarch-common-dao-UniversalDao.json:s8, javadoc-nablarch-common-dao-UniversalDao.json:s10, javadoc-nablarch-common-dao-UniversalDao.json:s11, javadoc-nablarch-common-dao-UniversalDao.json:s13