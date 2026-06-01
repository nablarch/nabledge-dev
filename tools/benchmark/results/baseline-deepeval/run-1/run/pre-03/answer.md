**結論**: UniversalDaoでDBを検索する方法は用途に応じて2種類あります。主キー検索はEntityクラスにJakarta Persistenceアノテーションを付けるだけで実行できます。任意条件の検索はSQLファイルを作成して `UniversalDao.findAllBySqlFile()` を使います。

**根拠**:

#### 事前設定

コンポーネント定義に `BasicDaoContextFactory` を追加します（JDBCラッパーの設定も別途必要）。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

#### ① 主キーを指定した検索（SQL不要）

`@Entity`・`@Id` アノテーションをEntityに付けると、SQLを書かずに主キー検索が可能です。SQL文は実行時に自動構築されます。

```java
// UniversalDaoの基本API（主キー検索例）
User user = UniversalDao.findById(User.class, userId);
```

対応するCRUD操作：主キーを指定した検索・更新・削除、登録 が利用できます。

#### ② 任意のSQL（SQLファイル）で検索する

検索条件が複雑な場合はSQLファイルを作成して `findAllBySqlFile()` を使います。

```java
// 条件なしで全件検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは検索結果をマッピングするBeanクラスから自動導出されます。例えば `sample.entity.User` クラスの場合、`sample/entity/User.sql`（クラスパス配下）に配置します。

#### ③ 検索条件を指定する

条件を持つ専用Beanを引数に渡します。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件には専用のBeanを使うのが原則ですが、単一テーブルのみアクセスする場合はEntityを直接指定しても構いません。

検索結果は `Bean`（Entity、Form、DTO）にマッピングされます。Beanのプロパティ名とSELECT句の名前が一致する項目が自動でマッピングされます。

#### ページング

`per()`・`page()` メソッドを先に呼び出すだけでページング検索が可能です。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報を取得する
Pagination pagination = users.getPagination();
```

#### 大量データの検索（遅延ロード）

大量データを扱う場合は `UniversalDao.defer()` を先に呼び出して遅延ロードを使用します。`DeferredEntityList` はサーバサイドカーソルを使用するため、必ず `close()` を呼び出す必要があります。

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
- 遅延ロード中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる場合があります。データベースベンダーのマニュアルを参照するか、ページングで回避してください。
- 主キー以外の条件を指定した更新・削除はUniversalDaoでは行えないため、その場合はデータベースアクセス（JDBCラッパー）を使用してください。
- Beanに使用できるデータタイプ（`String`、`Integer`、`Long`、`BigDecimal`、`java.sql.Date`、`java.time.LocalDate` など）に該当しない型はマッピングできません。

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s3, libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s9, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12