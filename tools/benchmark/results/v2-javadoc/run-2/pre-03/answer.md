セクション内容を確認できたので、回答を生成します。

**Step 6 verify**: 全Nablarchクレームをsections_contentで確認 — 全て直接記述あり。verify_result = PASS。

---

**結論**: UniversalDaoでの検索は、SQLファイルにSQLを記述してSQL IDを指定し、`UniversalDao.findAllBySqlFile()`を呼び出すのが基本です。主キーのみの単純な検索は、EntityにJakarta Persistenceアノテーションを付けるだけでSQLなしに実現できます。

**根拠**:

**1. 事前設定**

コンポーネント定義に`BasicDaoContextFactory`を追加する（JDBCラッパーの設定も別途必要）:

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**2. SQLファイルを使った検索（基本）**

SQLファイルを作成し、SQL IDを指定して検索する:

```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスはBeanのクラスから自動導出される（例: `sample.entity.User` → クラスパス配下の `sample/entity/User.sql`）。

**3. 条件を指定した検索**

検索条件を持つ専用のBeanを第3引数に渡す:

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

**4. ページング**

`per()`・`page()`メソッドを先に呼び出すだけで使用できる:

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination();
```

**5. 大量データの遅延ロード**

`defer()`メソッドを先に呼び出す。`DeferredEntityList`は必ずcloseが必要なので try-with-resources を使う:

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
- 検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目にマッピングされる
- 複数テーブルのJOIN検索は、個別に検索せず1本のSQLと結果をマッピングするBeanを用意する
- 遅延ロード中にトランザクション制御を行うとカーソルがクローズされる場合があるので注意

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s3, libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s8, libraries-universal-dao.json:s9, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12

---