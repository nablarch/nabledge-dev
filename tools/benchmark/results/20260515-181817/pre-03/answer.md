**結論**: UniversalDaoでデータベースを検索するには、主に3つの方法があります。①主キー検索（SQL不要）、②SQLファイルを使った検索、③条件付き検索です。

**根拠**:

### 1. 主キーを指定した検索（SQL不要）

Entityに`@Table`などのJakarta Persistenceアノテーションを付けるだけで、SQLを書かずに主キー検索ができます。SQLはアノテーションをもとに実行時に自動生成されます。

### 2. SQLファイルを使った検索

任意のSQLで検索したい場合は、SQLファイルを作成して`SQL ID`を指定します。

```java
// 基本的な使い方（SQL IDのみ指定）
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

- `User.class`が`sample.entity.User`の場合、SQLファイルは`sample/entity/User.sql`（クラスパス配下）
- 別クラスのSQLを使いたい場合は`#`で指定可能：

```java
UniversalDao.findAllBySqlFile(GoldUser.class, "sample.entity.Member#FIND_BY_NAME");
```

検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目に自動マッピングされます。

### 3. 条件を指定した検索

検索画面のように条件付き検索を行う場合は、条件をBeanとして渡します。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

### 4. 大量データの遅延ロード

大量データを扱う場合は`UniversalDao#defer()`を使って遅延ロードします。

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
- **設定が必要**: ユニバーサルDAOを使うには、コンポーネント定義に`BasicDaoContextFactory`の設定が必要です（`name="daoContextFactory"`）
- **検索条件はEntityではなく専用Beanを使う**: 複数テーブルにアクセスする場合は、検索条件専用のBeanを指定してください（1テーブルのみならEntityも可）
- **遅延ロードの注意**: 遅延ロード中にトランザクション制御を行うとカーソルがクローズされエラーになる場合があります。大量データ処理ではページングの併用も検討してください
- **スキーマ切り替え不可**: UniversalDaoのCRUD機能では、データベースアクセス(JDBCラッパー)の「SQL文中のスキーマを環境毎に切り替える」機能は使用できません

参照: `component/libraries/libraries-universal-dao.json#s2`, `component/libraries/libraries-universal-dao.json#s7`, `component/libraries/libraries-universal-dao.json#s10`, `component/libraries/libraries-universal-dao.json#s3`, `component/libraries/libraries-universal-dao.json#s6`, `component/libraries/libraries-universal-dao.json#s9`