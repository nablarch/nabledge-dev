**結論**: UniversalDaoでデータベースを検索するには、主に2つの方法があります。①主キーによる単純な検索（アノテーションのみ）、②SQLファイルを使った柔軟な検索（`findAllBySqlFile`）です。

**根拠**:

**① 主キーを指定した検索（SQLなし）**

EntityクラスにJakarta Persistenceアノテーション（`@Entity`、`@Id` など）を付けるだけで、主キーによる検索が可能です。SQLを書く必要はありません。

**② SQLファイルを使った検索**

任意の条件で検索するには `findAllBySqlFile` を使用します。

```java
// 全件検索（SQLファイル: sample/entity/User.sql）
List<User> users = UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、Beanのクラス名から自動的に導出されます（例: `sample.entity.User` → クラスパス配下の `sample/entity/User.sql`）。

**③ 検索条件を指定する場合**

```java
// フォームから検索条件を取得し、条件付き検索
ProjectSearchForm condition = context.getRequestScopedVar("form");
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

Beanのプロパティ名とSELECT句の名前が一致する項目が自動的にマッピングされます。

**④ 大量データの遅延ロード**

大量データを扱う場合は `UniversalDao.defer()` を使用して遅延ロードします。

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
- 条件付き検索では、Entityではなく検索条件専用のBeanを指定すること（1テーブルのみの場合はEntityも可）
- 複数テーブルのJOIN検索は、個別に検索するのではなく、1回のSQLとマッピング用Beanを作成すること
- 遅延ロード使用時は `DeferredEntityList#close` を必ず呼び出すこと（try-with-resources推奨）
- 遅延ロード中のトランザクション制御には注意が必要（RDBMSによってはカーソルがクローズされエラーになる可能性がある）

参照: `component/libraries/libraries-universal-dao.json#s3`, `component/libraries/libraries-universal-dao.json#s7`, `component/libraries/libraries-universal-dao.json#s10`, `component/libraries/libraries-universal-dao.json#s2`, `component/libraries/libraries-universal-dao.json#s9`