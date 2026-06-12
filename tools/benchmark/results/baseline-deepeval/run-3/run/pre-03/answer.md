**結論**: UniversalDaoでの検索は、主に `findAllBySqlFile` メソッドを使用してSQLファイルを呼び出す方法が基本です。主キー検索はSQLなしで実行でき、条件検索・ページング・遅延ロードにも対応しています。

---

**根拠**:

#### 1. 事前設定

コンポーネント定義に `BasicDaoContextFactory` を追加します。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

---

#### 2. 主キー検索（SQLファイル不要）

Entityに Jakarta Persistence アノテーションを付けるだけで、主キーを指定した検索が可能です。

```java
// 主キーでの検索（SQLファイル不要）
User user = UniversalDao.findById(User.class, userId);
```

---

#### 3. SQLファイルを使った全件/条件検索

任意のSQLで検索する場合は、SQLファイルを作成し SQL ID を指定します。

```java
// 全件検索（条件なし）
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、結果Beanのクラスパスから導出されます。例えば `sample.entity.User` クラスの場合、`クラスパス/sample/entity/User.sql` が読み込まれます。

**条件を指定した検索**では、検索条件用の専用Beanを第3引数に渡します（Entityではなく専用のBeanを使うこと）。

```java
// 検索条件Beanを用意
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// 条件付き検索
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", searchCondition);
```

検索結果は、Beanのプロパティ名とSELECT句のカラム名が一致する項目に自動マッピングされます。

**SQLファイル例**（動的条件の場合）:

```sql
SEARCH_PROJECT =
SELECT PROJECT_ID, PROJECT_NAME, PROJECT_START_DATE
FROM PROJECT
WHERE
    $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

---

#### 4. ページング検索

`per` メソッドと `page` メソッドを事前に呼び出すだけでページングが実現できます。

```java
EntityList<Project> projects = UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

// ページング情報の取得
Pagination pagination = projects.getPagination();
```

---

#### 5. 大量データの遅延ロード

大量データを扱う場合は `defer` メソッドを使い、`DeferredEntityList` を `close` する必要があります。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

---

**注意点**:
- 検索条件は、Entityではなく検索条件専用のBeanを用意すること（1テーブルへのアクセスのみの場合はEntityも可）
- `DeferredEntityList` は必ず `close` すること（サーバサイドカーソルを内部使用するため、closeしないとリソースリークになる）
- 遅延ロード中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる可能性がある

参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s3, libraries-universal-dao.json:s2, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, libraries-universal-dao.json:s6, web-application-getting-started-project-search.json:s1

---