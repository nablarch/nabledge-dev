Step 5: 回答を生成します。

**結論**: UniversalDaoでの検索は、SQLファイルに記述したSQLを`UniversalDao.findAllBySqlFile`で実行する方法が基本。Jakarta Persistenceアノテーション付きEntityを使えば、SQLなしで主キーによる検索も可能。

**根拠**:

### 1. 主キーによる検索（SQLなし）

Jakarta Persistenceアノテーションを付与したEntityがあれば、SQLを書かずに主キー指定の検索が可能。

### 2. SQLファイルを使った検索

SQLファイルを作成し、SQL IDを指定して検索する:

```java
// 全件取得
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、検索結果をマッピングするBeanクラスから導出される。`sample.entity.User` クラスであれば、`sample/entity/User.sql` が対象。

### 3. 条件を指定した検索

検索条件はEntityではなく、専用のBeanを使う:

```java
// 検索条件Beanを取得
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

### 4. ページングを伴う検索

`per`（1ページ件数）と`page`（ページ番号）を先に呼び出す:

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

### 5. 遅延ロード（大量データ向け）

大量データを扱う場合は`defer()`を先に呼び出し、`DeferredEntityList`を`close`する:

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
- 検索条件にはEntityではなく専用のBeanを使うこと（1テーブルのみのアクセスでは例外的にEntity可）
- 遅延ロード使用時は必ず`DeferredEntityList#close`を呼ぶこと（内部でサーバサイドカーソルを使用しているため）
- RDBMSによっては、遅延ロード中のトランザクション制御でカーソルがクローズされる場合がある

参照: `libraries-universal-dao.json:s2`, `libraries-universal-dao.json:s3`, `libraries-universal-dao.json:s7`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s10`, `libraries-universal-dao.json:s12`

---