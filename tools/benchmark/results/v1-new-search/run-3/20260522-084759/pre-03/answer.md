回答を生成します。

---

**結論**: UniversalDaoでの検索は `UniversalDao.findAllBySqlFile()` を使ってSQLファイルで検索する方法と、Entityに`@Id`等のJakarta PersistenceアノテーションをつけてSQLを自動生成する方法の2種類があります。

**根拠**:

**1. 事前設定（コンポーネント定義に追加）**

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**2. 主キーを指定した検索（SQL自動生成）**

`@Entity`、`@Id` などJakarta PersistenceアノテーションをEntityに付けると、主キー指定の検索が自動生成SQLで実行できます。

**3. SQLファイルを使った検索**

```java
// 全件検索（条件なし）
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルは検索結果をマッピングするBeanクラスから導出されます。`sample.entity.User` の場合、クラスパス配下の `sample/entity/User.sql` が使われます。

**4. 条件を指定して検索**

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件は専用のBeanを指定します（単一テーブルの場合はEntityも可）。

**5. ページングを行う**

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報（件数など）の取得
Pagination pagination = users.getPagination();
```

**6. 大量データを扱う場合（遅延ロード）**

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
- 遅延ロードは内部でサーバサイドカーソルを使用するため、`DeferredEntityList#close` の呼び出しが必要です（try-with-resourcesを使うと自動でクローズされます）
- 検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目にマッピングされます
- JOINした検索結果を取得する場合も、1回のSQLとマッピング用Beanを用意して `findAllBySqlFile` で取得します

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s3, libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s9, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12

---