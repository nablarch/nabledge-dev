**結論**: UniversalDaoでデータベースを検索するには、主に2つの方法があります。①主キーを使った簡易検索（SQLファイル不要）と、②SQLファイルを作成して任意の条件で検索する方法です。

**根拠**:

**方法1: 主キーを指定した検索（SQLファイル不要）**

EntityクラスにJakarta Persistenceアノテーション（`@Entity`、`@Id`、`@Column` など）を付けることで、SQLを書かずに主キー検索が可能です。

```java
User user = UniversalDao.findById(User.class, userId);
```

**方法2: SQLファイルを使った任意の条件検索**

任意のSQLで検索したい場合は、SQLファイルを作成してSQL IDを指定します。検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目に自動マッピングされます。

```java
// 全件検索
List<User> users = UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");

// 検索条件を渡す場合
ProjectSearchForm condition = context.getRequestScopedVar("form");
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

SQLファイルのパスはBeanクラスから導出されます。`sample.entity.User` クラスであれば、クラスパス配下の `sample/entity/User.sql` が対象です。

**方法3: 大量データの遅延ロード**

大量の検索結果をメモリに一括展開できない場合は、`defer()` で遅延ロードできます。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**方法4: ページング検索**

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination();
```

**注意点**:
- UniversalDaoを使用するには、`BasicDaoContextFactory` のコンポーネント定義が必要です。
- 検索条件はEntityではなく、専用の検索条件Beanを使用することが推奨されます。
- 遅延ロードでは `DeferredEntityList#close` の呼び出しが必要です（try-with-resources推奨）。
- 悲観的ロック（SELECT FOR UPDATE）が必要な場合は `UniversalDao#findBySqlFile` を使用します。
- 主キー以外の条件を使った更新・削除はUniversalDaoでは対応していないため、JDBCラッパーを使用してください。

参照: `component/libraries/libraries-universal-dao.json#s2`, `#s3`, `#s7`, `#s9`, `#s10`, `#s12`