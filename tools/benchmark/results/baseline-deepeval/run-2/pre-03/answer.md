セクション内容を読み込みました。Step 5で回答を生成します。

---

**結論**: UniversalDaoでの検索は主に `UniversalDao.findAllBySqlFile()` を使い、SQLファイルにSQL IDを定義して呼び出します。条件指定・ページング・遅延ロードもメソッドチェーンで簡潔に記述できます。

**根拠**:

### 1. 事前設定

`BasicDaoContextFactory` をコンポーネント定義に追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

### 2. 基本検索（SQLファイル使用）

SQLファイル（クラスパス配下に配置）にSQL IDを定義し、`findAllBySqlFile` で呼び出します。

**SQLファイル例** (`sample/entity/User.sql`):
```sql
FIND_BY_NAME =
SELECT
    USER_ID,
    USER_NAME
FROM
    USER
WHERE
    USER_NAME = :userName
```

**呼び出し例**:
```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

検索結果はBeanのプロパティ名とSELECT句の名前が一致する項目に自動マッピングされます。

### 3. 条件を指定して検索する

検索条件はEntityではなく専用の検索条件Beanを使います。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

可変条件には `$if` 構文を使います。

```sql
SEARCH_PROJECT =
SELECT PROJECT_ID, PROJECT_NAME
FROM PROJECT
WHERE
    $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
```

### 4. ページング検索

`per()` と `page()` をチェーンして呼び出します。

```java
EntityList<Project> projects = UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

// ページング情報の取得
Pagination pagination = projects.getPagination();
```

### 5. 大量データの遅延ロード

メモリに全件展開できない場合は `defer()` を使います。必ず `close()` が必要です。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

### 6. 主キー検索（SQL不要）

Entityに Jakarta Persistence アノテーションを付けるだけで、SQLを書かずに主キー検索ができます。

**注意点**:
- 遅延ロード中はトランザクション制御を行うとカーソルがクローズされエラーになる可能性があります
- 検索条件BeanのプロパティはカラムのJava型（`java.sql.Date` など）に合わせて定義します（フォームはString型のまま、`BeanUtil.createAndCopy` で変換）
- SQLファイルは機能ごとに作成し、複数機能で流用しないでください

参照: `libraries-universal-dao.json:s2`, `libraries-universal-dao.json:s6`, `libraries-universal-dao.json:s7`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s10`, `libraries-universal-dao.json:s12`, `web-application-getting-started-project-search.json:s1`

---