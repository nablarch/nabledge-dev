**結論**: UniversalDaoでデータベースを検索するには、`UniversalDao.findAllBySqlFile()` にBeanクラスとSQL IDを指定して呼び出します。条件を指定する場合は検索条件Beanを第3引数に渡します。

**根拠**:

**1. 事前設定**

コンポーネント定義ファイルに `BasicDaoContextFactory` を追加します（[データベースアクセス(JDBCラッパー)](../../../component/libraries/libraries-database.json) の設定も別途必要）。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**2. SQLファイルを使った基本的な検索**

SQLファイルにSQL IDを定義し、Beanクラスと SQL ID を指定して検索します。

```java
// Beanクラスから自動的にSQLファイルパスが導出される
// (例) sample.entity.User -> クラスパス配下の sample/entity/User.sql
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

**3. 条件を指定した検索**

検索条件をBeanに設定し、第3引数として渡します。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件のBeanは、Entityではなく専用の検索条件Beanを使用すること（1テーブルのみの場合はEntityも可）。

**4. ページングを行う検索**

```java
EntityList<User> users = UniversalDao.per(20L).page(1L)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
// ページング情報の取得
Pagination pagination = users.getPagination();
```

**5. 大量データの遅延ロード検索**

大量データ処理ではメモリ節約のため遅延ロードを使用します。`DeferredEntityList#close` を必ず呼び出す必要があります。

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
- 遅延ロード中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる場合があります。
- 大量バイナリデータ（BLOB等）は `byte[]` でBeanにマッピングするとメモリが枯渇するため、直接 [データベースアクセス(JDBCラッパー)](../../../component/libraries/libraries-database.json) を使用してください。

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  任意のSQL(SQLファイル)で検索する
  条件を指定して検索する
  ユニバーサルDAOを使うための設定を行う
  検索結果を遅延ロードする
  ページングを行う
- 検索機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md
  検索する