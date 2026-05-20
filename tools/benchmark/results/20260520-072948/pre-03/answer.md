**結論**: UniversalDaoでの検索には、主キー検索・SQLファイルによる全件/条件付き検索の3つの方法があります。マスタテーブルの場合は `UniversalDao.findAllBySqlFile()` でSQLファイルを使った検索が基本です。

**根拠**:

**1. 主キーを指定した検索（SQLなし）**

EntityにJakarta Persistenceアノテーションを付けるだけで、主キー検索が可能です。

```java
// 主キーを指定してBOOKテーブルから1件取得（例）
Book book = UniversalDao.findById(Book.class, bookId);
```

**2. SQLファイルによる検索（全件）**

任意のSQLで検索する場合は、SQLファイルを作成し、SQL IDを指定します。

```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、マッピングするBeanクラス（例: `sample.entity.User`）から `sample/entity/User.sql` として導出されます。

**3. 条件を指定した検索**

検索条件Beanを渡すことで、条件付き検索ができます。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件には、Entityではなく専用の条件BeanまたはFormを指定します（1テーブルのみの場合はEntityでも可）。

**検索結果のマッピング**: BeanのプロパティとSELECT句の名前が一致する項目が自動でマッピングされます。

**注意点**:
- ユニバーサルDAOを使うには、コンポーネント定義に `BasicDaoContextFactory` の設定が必要です。
  ```xml
  <component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
  ```
- 主キー以外の条件を指定した更新・削除はユニバーサルDAOではできません。その場合はJDBCラッパーを使用してください。

参照: component/libraries/libraries-universal-dao.json:s2, s3, s6, s7, s10