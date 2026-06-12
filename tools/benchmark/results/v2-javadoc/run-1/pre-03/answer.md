Javadocセクションはs1のみで内容が薄いので、主要知識はuniversal-dao.jsonから取得できました。Step 5: 回答を生成します。

---

**結論**: UniversalDaoでデータベースを検索するには、`UniversalDao.findAllBySqlFile()` メソッドでSQLファイルを指定する方法と、主キー検索の場合はSQLなしでEntity情報から自動生成する方法の2つがあります。

**根拠**:

### 1. 事前設定

コンポーネント定義に `BasicDaoContextFactory` を追加します（データベースアクセス(JDBCラッパー)の設定も別途必要）。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

### 2. 主キーを指定した検索（SQLなし）

`@Id` アノテーションが付いた主キーで1件検索する場合は、`UniversalDao.findById()` を使います。SQLを書く必要はありません（Jakarta PersistenceアノテーションをEntityに付けるだけでSQLが実行時に自動生成されます）。

---

### 3. 任意のSQLファイルで検索（全件・条件指定）

SQLファイルを作成し、SQL IDを指定して検索します。

**全件取得**:
```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスはBeanクラスから導出されます（例: `sample.entity.User` の場合 → クラスパス配下の `sample/entity/User.sql`）。

**検索条件を指定**:
```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件は、Entityではなく検索条件専用のBeanを指定してください（1テーブルのみのアクセスの場合はEntityを指定しても良い）。

---

### 4. 検索結果のBeanマッピング

検索結果はBean（Entity、Form、DTO）にマッピングされます。**Beanのプロパティ名とSELECT句の名前が一致する項目**が自動的にマッピングされます。

使用できるデータタイプ: `String`, `Integer`, `Long`, `BigDecimal`, `Boolean`, `java.sql.Date`, `java.sql.Timestamp`, `LocalDate`, `LocalDateTime`, `byte[]` など。

---

### 5. ページング

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報の取得
Pagination pagination = users.getPagination();
```

---

### 6. 大量データの遅延ロード

大量データを処理する場合（バッチやダウンロード）は、`UniversalDao.defer()` を先に呼び出し、`DeferredEntityList` を try-with-resources で必ずcloseしてください。

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
- `defer()` 使用中はサーバサイドカーソルが開きます。RDBMSによってはカーソルオープン中にトランザクション制御を行うとカーソルがクローズされエラーになる場合があります。
- Beanに記載のないデータタイプにマッピングしようとすると実行時例外が発生します。
- ユニバーサルDAOで実現できない場合（主キー以外の条件での更新/削除など）は、データベースアクセス(JDBCラッパー)を直接使用してください。

参照: `libraries-universal-dao.json:s6`, `libraries-universal-dao.json:s7`, `libraries-universal-dao.json:s10`, `libraries-universal-dao.json:s2`, `libraries-universal-dao.json:s3`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s12`, `libraries-universal-dao.json:s25`

---