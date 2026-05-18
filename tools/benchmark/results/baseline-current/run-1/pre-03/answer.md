**結論**: UniversalDaoでのデータ検索には、主に「主キーを使った検索」と「SQLファイルを使った検索（条件指定含む）」の2つの方法があります。

**根拠**:

**1. 主キーを指定した検索（SQLファイル不要）**

EntityにJakarta Persistenceアノテーション（`@Entity`, `@Id`, `@Column` など）を付けることで、SQLを書かずに主キー検索ができます。SQL文は実行時に自動構築されます。

**2. SQLファイルを使った検索**

任意のSQLで検索する場合は、SQLファイルを作成し `findAllBySqlFile` を使用します。

```java
// 基本的な検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、マッピング先のBeanクラスから自動導出されます（例: `sample.entity.User` → `sample/entity/User.sql`）。

**3. 条件を指定した検索**

検索条件を持つBeanを渡すことで、条件付き検索ができます。

```java
ProjectSearchForm condition = context.getRequestScopedVar("form");

List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件は、Entityではなく専用のBeanを指定することが推奨されます（1テーブルのみの場合はEntityも可）。

**4. 大量データの遅延ロード**

大量検索結果を扱う場合は `defer()` で遅延ロードを使用します。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

`DeferredEntityList#close` の呼び出しが必要なため、try-with-resourcesを使います。

**注意点**:
- UniversalDaoは簡易的なO/Rマッパーであり、主キー以外の条件を指定した更新/削除はできません。その場合はデータベースアクセス（JDBCラッパー）を使用してください。
- 遅延ロード使用中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる場合があります。
- ユニバーサルDAOを使用するには、`BasicDaoContextFactory` のコンポーネント定義への追加が必要です（`daoContextFactory` というコンポーネント名で設定）。

参照: `knowledge/component/libraries/libraries-universal-dao.json#s2`, `#s3`, `#s7`, `#s9`, `#s10`