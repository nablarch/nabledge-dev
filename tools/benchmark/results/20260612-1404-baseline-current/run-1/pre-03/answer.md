**結論**: UniversalDaoでのデータベース検索は、主キー検索には `UniversalDao.findById`、SQLファイルを使った柔軟な検索には `UniversalDao.findAllBySqlFile` を使用します。

**根拠**:

**① 主キーで1件検索**

```java
// 主キーを指定して1件取得（該当なしの場合はNoDataException）
User user = UniversalDao.findById(User.class, userId);

// 該当なしの場合にnullを返す場合
User user = UniversalDao.findByIdOrNull(User.class, userId);
```

**② SQLファイルで複数件検索**

SQLファイル（`sample/entity/User.sql`）に `FIND_BY_NAME` というSQL IDを定義し:

```java
// 条件なし
EntityList<User> users = UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");

// 条件を指定（Beanのプロパティ名をバインド変数に使用）
ProjectSearchDto condition = new ProjectSearchDto();
condition.setProjectName("test");
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

SQLファイルのパスは、第1引数のクラス（例：`sample.entity.User`）からクラスパス配下の `sample/entity/User.sql` として導出されます。

**③ ページング検索**

```java
EntityList<User> users = UniversalDao.per(20).page(1)
    .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページネーション情報の取得
Pagination pagination = users.getPagination();
```

**④ 大量データの遅延ロード（バッチ等）**

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
- 遅延ロードではサーバサイドカーソルを使用するため、`DeferredEntityList#close` の呼び出しが必要です（try-with-resources推奨）
- カーソルオープン中にトランザクション制御を行うとカーソルがクローズされる場合があるため、使用するRDBMSのマニュアルを確認してください
- 主キー以外の条件を指定した更新・削除はUniversalDaoでは行えないため、その場合はデータベースアクセス(JDBCラッパー)を使用してください

参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s9, libraries-universal-dao.json:s12, javadoc-nablarch-common-dao-UniversalDao.json:s8, javadoc-nablarch-common-dao-UniversalDao.json:s11, web-application-getting-started-project-search.json:s1