**結論**: `UniversalDao.findAllBySqlFile()` メソッドを使い、SQLファイルとSQL IDを指定して検索するのが基本です。主キーによる単純な検索も SQL を書かずに実行できます。

**根拠**:

**① 主キーを指定した検索（SQLなし）**

Entityに `@Entity`、`@Id` などの Jakarta Persistence アノテーションを付けるだけで、SQL を書かずに主キー指定の検索が実行できます。

**② SQLファイルを使った検索（基本パターン）**

SQLファイルを作成し、SQL IDを指定して検索します:

```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは検索結果の Bean クラスから自動導出されます（例: `sample.entity.User` → `sample/entity/User.sql`）。

**③ 条件を指定した検索**

検索条件 Bean を第3引数として渡します:

```java
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

`condition` は検索条件を保持する専用の Bean（Entity とは別の DTO）を使います。Bean のプロパティ名に対応した `:propertyName` バインド変数が SQL に自動的にバインドされます。

**④ ページング付き検索**

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

**⑤ 大量データの遅延ロード**

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 処理
    }
}
```

遅延ロード使用時は `DeferredEntityList#close` を必ず呼び出すこと（`try-with-resources` 推奨）。

**設定**

コンポーネント定義ファイルに `BasicDaoContextFactory` の設定が必要です:

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- 検索結果をマッピングする Bean のプロパティ名は SELECT 句の列名と一致させる必要があります
- 遅延ロード中にトランザクション制御を行うと、RDBMS によってはカーソルがクローズされエラーになる場合があります
- 主キー以外の条件による更新/削除はユニバーサルDAOでは行えないため、データベースアクセス(JDBCラッパー)を使用します

参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, libraries-universal-dao.json:s6, web-application-getting-started-project-search.json:s1