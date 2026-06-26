**結論**:
`UniversalDao` クラスの静的メソッドを使って検索します。主キー検索は `findById`、SQLファイルを使った条件検索は `findAllBySqlFile` / `findBySqlFile` を使用します。

**根拠**:

**① 主キーで1件検索**

```java
// 1件取得（0件の場合 NoDataException）
User user = UniversalDao.findById(User.class, userId);

// 1件取得（0件の場合 null）
User user = UniversalDao.findByIdOrNull(User.class, userId);
```

**② 全件取得**

```java
EntityList<User> users = UniversalDao.findAll(User.class);
```

**③ SQLファイルを使った条件検索（複数件）**

```java
// 検索条件をBeanで渡す
Book condition = new Book();
condition.setAuthor("Martin Fowler");

EntityList<Book> books = UniversalDao.findAllBySqlFile(Book.class, "FIND_BY_AUTHOR", condition);
```

SQLファイルに定義した SQL_ID（例: `FIND_BY_AUTHOR`）を指定し、バインド変数はBeanのプロパティとして渡します。

**④ SQLファイルを使った条件検索（1件）**

```java
Book condition = new Book();
condition.setId(1L);

Book book = UniversalDao.findBySqlFile(Book.class, "FIND_BY_ID", condition);
```

**⑤ ページング**

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

Pagination pagination = users.getPagination();
```

`per(1ページあたりの件数).page(ページ番号)` を先に呼び出すだけで使えます。

**⑥ 遅延ロード（大量データ）**

大量データを扱う場合は `defer()` を使います。`DeferredEntityList` は必ず `close()` が必要です。

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
- `findById` / `findBySqlFile` は0件の場合 `NoDataException` をスローします。0件をnullで受け取りたい場合は `findByIdOrNull` / `findBySqlFileOrNull` を使用してください。
- 遅延ロード使用中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされてエラーとなる場合があります。

参照: libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, javadoc-nablarch-common-dao-UniversalDao.json:s8, javadoc-nablarch-common-dao-UniversalDao.json:s9, javadoc-nablarch-common-dao-UniversalDao.json:s10, javadoc-nablarch-common-dao-UniversalDao.json:s11, javadoc-nablarch-common-dao-UniversalDao.json:s12, javadoc-nablarch-common-dao-UniversalDao.json:s13, javadoc-nablarch-common-dao-UniversalDao.json:s14