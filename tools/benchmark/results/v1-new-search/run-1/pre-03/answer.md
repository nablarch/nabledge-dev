**結論**: UniversalDaoでの検索には、主キー指定の単純検索とSQLファイルを使った柔軟な検索の2種類があります。SQLファイルを使う場合は `UniversalDao.findAllBySqlFile` メソッドで検索結果をBeanにマッピングして取得できます。

**根拠**:

**1. 主キーを指定した検索（SQLファイル不要）**

Entityに `@Entity`、`@Id` などのJakarta Persistenceアノテーションを付与するだけで、SQL不要で主キー検索ができます。

**2. 任意のSQLファイルで検索する**

SQLファイルを作成し、SQL IDを指定して検索します。検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目に自動でマッピングされます。

```java
// 全件検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、マッピング対象Beanのクラス名から自動導出されます（例: `sample.entity.User` → クラスパス配下の `sample/entity/User.sql`）。

**3. 条件を指定して検索する**

検索条件をBeanで渡す場合は、第3引数に条件Beanを指定します。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件は専用のBeanを使用してください（単一テーブルへのアクセスの場合はEntityを指定しても構いません）。

**4. ページングを行う**

`UniversalDao.per` と `UniversalDao.page` を先に呼び出します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

**5. 大量データを遅延ロードする**

大量データを処理する場合は `UniversalDao.defer` を使います。内部でサーバサイドカーソルを使用するため、`DeferredEntityList#close` の呼び出しが必要です。

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
- ユニバーサルDAOを使用するには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要です。
  ```xml
  <component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
  ```
- 遅延ロード中にトランザクション制御を行うと、使用するRDBMSによってはカーソルがクローズされエラーになる場合があります。
- 大量のバイナリデータはユニバーサルDAOでメモリ展開せず、データベースアクセス（JDBCラッパー）を直接使用してください。

参照: `libraries-universal-dao.json:s2`, `libraries-universal-dao.json:s3`, `libraries-universal-dao.json:s6`, `libraries-universal-dao.json:s7`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s10`, `libraries-universal-dao.json:s12`