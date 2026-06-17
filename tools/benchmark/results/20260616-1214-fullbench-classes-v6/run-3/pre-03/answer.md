**結論**: UniversalDaoでデータベースを検索するには、主キー検索なら `UniversalDao.findById()` を、任意のSQL検索なら `UniversalDao.findAllBySqlFile()` を使用します。

**根拠**:

**① 主キーを指定した検索（SQLファイル不要）**

EntityクラスにJakarta Persistenceアノテーション（`@Entity`、`@Id` など）を付けるだけで、SQLを書かずに主キー検索できます。

```java
// 主キーを指定して1件取得
User user = UniversalDao.findById(User.class, userId);
```

**② 任意のSQL（SQLファイル）で検索する**

SQLファイルを作成し、SQL IDを指定して検索します。

```java
// 全件検索（条件なし）
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルはBeanのクラス名から自動導出されます（例：`sample.entity.User` → `sample/entity/User.sql`）。

**③ 条件を指定して検索する**

条件BeanをSQLファイル検索の第3引数に渡します。

```java
// 検索条件Beanを指定
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件はEntityではなく専用のBeanを使うことが推奨です（1テーブルのみの場合はEntityも可）。

**④ ページングを行う場合**

`per()` と `page()` を先に呼び出します。

```java
EntityList<Project> projects = UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

ページング情報（件数等）は `EntityList#getPagination()` で取得できます。

**⑤ 大量データを扱う場合（遅延ロード）**

`defer()` を使ってサーバサイドカーソルで1件ずつ処理できます。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

**注意点**:
- 遅延ロード中にトランザクション制御が行われると、RDBMSによってはカーソルがクローズされエラーになる場合があります。try-with-resources で `DeferredEntityList#close()` を必ず呼び出してください。
- UniversalDAOは簡易O/Rマッパーであり、主キー以外の条件での更新・削除は対応していません（その場合はデータベースアクセス（JDBCラッパー）を使用）。

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9