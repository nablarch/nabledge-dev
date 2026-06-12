**結論**: UniversalDaoで検索するには、主キー検索はEntityのJakarta Persistenceアノテーションだけで実行でき、任意条件の検索は `UniversalDao.findAllBySqlFile()` にSQL IDを指定して実行します。

**根拠**:

**① 主キーを指定した検索（SQLファイル不要）**

Jakarta PersistenceアノテーションをEntityに付けるだけで、SQLを書かずに主キー指定の検索ができます（SQL文は実行時に自動構築）。

**② SQLファイルで検索する**

任意のSQLで検索したい場合は、SQLファイルを作成してSQL IDを指定します。

```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは検索結果のマッピング先クラスから導出されます。例えば `sample.entity.User` の場合、クラスパス配下の `sample/entity/User.sql` が対象です。

別クラスのSQLを使う場合は `#` で指定できます。

```java
UniversalDao.findAllBySqlFile(GoldUser.class, "sample.entity.Member#FIND_BY_NAME");
```

**③ 条件を指定して検索する**

検索条件Beanを第3引数に渡せます。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件には、Entityではなく専用の条件Beanを指定してください（1テーブルのみの場合はEntityも可）。

**④ ページングを行う**

`per()` と `page()` を先に呼び出すだけでページングできます。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

ページング情報（件数など）は `Pagination` オブジェクトから取得できます。

```java
Pagination pagination = users.getPagination();
```

**⑤ 大量データの遅延ロード**

大量データ処理では `defer()` を使って遅延ロードします。内部でサーバサイドカーソルを使用するため、必ず `close()` を呼び出してください。

```java
// try-with-resourcesを使ったclose呼び出し。
// DeferredEntityListはダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**注意点**:
- 遅延ロード中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる場合があります。大量データ処理中はトランザクション制御に注意するか、ページングで回避してください。
- JOIN検索が必要な場合は、個別に検索せず1回で取得できるSQLとマッピング用Beanを作成してください。

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s9, libraries-universal-dao.json:s12