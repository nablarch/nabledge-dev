これで必要な情報が揃いました。Step 5〜8の回答を生成します。

---

**結論**: UniversalDaoでの検索は、主キー検索であれば `UniversalDao.findById()` を、SQLファイルを使った任意条件の検索であれば `UniversalDao.findAllBySqlFile()` を使用します。

**根拠**:

### 1. 主キーを指定した検索（SQLファイル不要）

Entityに `@Entity`、`@Id` などのJakarta Persistenceアノテーションを付けるだけで、SQLを書かずに主キー検索が可能です。

```java
// 主キーを指定して1件取得（Userエンティティの例）
User user = UniversalDao.findById(User.class, userId);
```

### 2. SQLファイルを使った検索

任意の条件で検索したい場合は、SQLファイルを作成してSQL IDを指定します。

```java
// 全件取得
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、マッピング先Beanのクラスパスから導出されます（例：`sample.entity.User` → `sample/entity/User.sql`）。

### 3. 条件を指定した検索

検索画面のように動的な条件を指定する場合は、第3引数に検索条件Beanを渡します。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件は、Entityではなく検索条件専用のBeanを指定します（1つのテーブルのみの場合はEntityでも可）。

### 4. ページングを使った検索

ページングは `per()` と `page()` を前置するだけで使用できます。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページネーション情報の取得
Pagination pagination = users.getPagination();
```

### 5. 大量データの遅延ロード

大量データを扱う場合は `defer()` を使い、`DeferredEntityList` を `try-with-resources` でcloseします。

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
- 遅延ロード中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーとなる場合があります
- 使用前にコンポーネント定義に `BasicDaoContextFactory` の設定が必要です:
  ```xml
  <component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
  ```
- 検索結果はBean（Entity、Form、DTO）にマッピングされ、Beanのプロパティ名とSELECT句の名前が一致する項目がマッピングされます

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s3, libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s9, libraries-universal-dao.json:s12

---