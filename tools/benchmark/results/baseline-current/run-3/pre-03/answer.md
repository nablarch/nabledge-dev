**結論**: UniversalDaoでのデータ検索には、主に2つの方法があります。①主キー指定の自動生成SQLによる検索（SQLファイル不要）、②SQLファイルを作成してSQL IDを指定する任意の検索です。

**根拠**:

### 方法1: 主キーを指定した検索（SQLファイル不要）

`@Entity` などのJakarta PersistenceアノテーションをEntityに付けるだけで、主キーを指定した検索がSQLを書かずに利用できます。

```java
// 主キーで1件検索
User user = UniversalDao.findById(User.class, userId);
```

### 方法2: SQLファイルを使った任意の検索

SQLファイルを作成し、SQL IDを指定して検索します。検索結果はBean（Entity、Form、DTO）のプロパティ名とSELECT句の名前が一致する項目に自動マッピングされます。

```java
// SQLファイルで全件検索（User.classの場合、sample/entity/User.sqlを参照）
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");

// 別ファイルのSQLを指定する場合（#で区切る）
UniversalDao.findAllBySqlFile(GoldUser.class, "sample.entity.Member#FIND_BY_NAME");
```

### 方法3: 条件を指定して検索

検索画面など条件付き検索には、検索条件Beanを引数として渡します。

```java
// 検索条件Beanを取得
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

> 検索条件はEntityではなく専用のBeanを使うこと（1テーブルのみの場合はEntityも可）

### ページング検索

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination(); // ページング情報取得
```

### 大量データの遅延ロード

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

### 事前設定

利用前に `BasicDaoContextFactory` をコンポーネント定義に追加する必要があります。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**注意点**:
- 主キー以外の条件を指定した更新/削除はUniversalDaoでは行えないため、その場合はJDBCラッパーを使うこと
- 遅延ロードでは `DeferredEntityList#close` を必ず呼び出すこと（try-with-resources推奨）
- RDBMSによっては、遅延ロード中のトランザクション制御でカーソルがクローズされエラーになる場合があるため注意すること
- 共通項目（登録ユーザ、更新日時等）の自動設定機能はUniversalDaoでは提供されていない

参照: `component/libraries/libraries-universal-dao.json#s2`, `#s3`, `#s6`, `#s7`, `#s9`, `#s10`, `#s12`