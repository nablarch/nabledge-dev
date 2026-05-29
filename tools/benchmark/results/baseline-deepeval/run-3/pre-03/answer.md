これで回答を生成します。

---

**結論**: UniversalDaoでDBデータを検索するには、主キー指定の場合は`UniversalDao.findById`を、任意のSQLの場合は`UniversalDao.findAllBySqlFile`を使います。検索結果はBean（Entity/Form/DTO）に自動マッピングされます。

**根拠**:

### 1. 主キーを指定した検索（SQLなし）

`@Entity` などのJakarta PersistenceアノテーションをEntityに付けるだけで、SQLを書かずに主キー検索できます。

```java
// 主キーを指定して1件取得
User user = UniversalDao.findById(User.class, userId);
```

### 2. 任意のSQL（SQLファイル）で検索する

SQLファイルを作成し、SQL IDを指定して検索します。

```java
// 全件取得
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、マッピングするBeanクラスから導出されます。  
例: `sample.entity.User` → クラスパス配下の `sample/entity/User.sql`

### 3. 条件を指定して検索する

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件は、Entityではなく検索条件を持つ専用のBeanを指定する。ただし、1つのテーブルのみへのアクセスの場合は、Entityを指定しても良い。

### 4. ページングを行う

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報を取得
Pagination pagination = users.getPagination();
```

### 5. 大量データの遅延ロード

```java
// try-with-resourcesを使ったclose呼び出し
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

### 事前設定

コンポーネント定義ファイルに `BasicDaoContextFactory` を追加します。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- 遅延ロードでは内部でサーバサイドカーソルを使用するため、`DeferredEntityList#close`を必ず呼び出すこと（try-with-resources推奨）
- 遅延ロード中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーとなる場合があるため注意

参照: `libraries-universal-dao.json:s2`, `libraries-universal-dao.json:s3`, `libraries-universal-dao.json:s7`, `libraries-universal-dao.json:s10`, `libraries-universal-dao.json:s6`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s12`

---