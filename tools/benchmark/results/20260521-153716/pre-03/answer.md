Step 5〜7を実行して回答を生成します。

---

**結論**: UniversalDaoでのデータ検索は、主キー検索（SQL不要）と `UniversalDao.findAllBySqlFile` メソッドを使ったSQLファイル指定検索の2通りで実装できます。

**根拠**:

**1. 事前設定**

コンポーネント定義に `BasicDaoContextFactory` を追加します。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**2. 主キーを指定した検索（SQL不要）**

Entityに Jakarta Persistence アノテーション（`@Entity`、`@Id`、`@Column` 等）を付けるだけで、主キー検索が可能です。SQL文は実行時に自動構築されます。

**3. SQLファイルによる検索**

任意のSQLで検索する場合は、SQLファイルを作成し `findAllBySqlFile` を使用します。

```java
// 全件検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスはBeanクラスから導出されます（例: `sample.entity.User` → `sample/entity/User.sql`）。

**4. 条件を指定して検索**

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件には、専用のBean（Formクラス等）を指定します。1テーブルのみの場合はEntityを指定しても構いません。

検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目に自動マッピングされます。

**5. ページング**

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページ情報の取得
Pagination pagination = users.getPagination();
```

`per`（1ページあたりの件数）、`page`（ページ番号）を先に呼び出すだけで使用できます。

**注意点**:
- 大量データを処理する場合は遅延ロード（`UniversalDao.defer()`）を使用し、`DeferredEntityList#close` を必ず呼び出してカーソルをクローズすること。
- 主キー以外の条件を指定した更新・削除はUniversalDaoでは行えないため、その場合はデータベースアクセス（JDBCラッパー）を使用すること。

参照: `libraries-universal-dao.json:s2`, `libraries-universal-dao.json:s3`, `libraries-universal-dao.json:s6`, `libraries-universal-dao.json:s7`, `libraries-universal-dao.json:s10`, `libraries-universal-dao.json:s12`, `libraries-universal-dao.json:s9`

---