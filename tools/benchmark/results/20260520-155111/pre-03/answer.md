**結論**: UniversalDaoでの検索には、主キー指定検索（自動SQL生成）とSQLファイルを指定した全件/条件検索の2パターンがあります。いずれも `UniversalDao` クラスのメソッドを呼び出すだけで実装できます。

**根拠**:

**① 主キーを指定した検索（SQL不要）**

EntityクラスにJakarta Persistenceアノテーション（`@Entity`、`@Id`、`@Column`等）を付けることで、SQLを書かずに主キー検索が実行できます。

```java
// 主キーで1件取得（UniversalDaoの基本API参照）
User user = UniversalDao.findById(User.class, userId);
```

**② SQLファイルで全件検索**

検索条件なしで全件取得する場合は `findAllBySqlFile` を使用します。

```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスはBeanクラスから導出されます。`sample.entity.User` クラスなら、クラスパス配下の `sample/entity/User.sql` が使われます。

**③ 条件を指定した検索**

検索条件（Form等）を渡す場合は第3引数に指定します。

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件はEntityではなく専用のBeanを使うことが推奨されます（単一テーブルのみの場合はEntityも可）。

**④ 結果をBeanにマッピングする仕組み**

検索結果は、Beanのプロパティ名とSELECT句の名前が一致する項目に自動でマッピングされます。Entity以外にもFormやDTOにマッピング可能です。

**注意点**:
- ユニバーサルDAOを使用するには、データベースアクセス(JDBCラッパー)の設定に加えて、コンポーネント定義に `BasicDaoContextFactory` の設定が必要です。
  ```xml
  <component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
  ```
- 主キー以外の条件を指定した更新・削除はユニバーサルDAOでは行えません。その場合はデータベースアクセス(JDBCラッパー)を使用してください。
- 大量データを扱う場合は遅延ロード（`UniversalDao.defer()`）やページング（`UniversalDao.per().page()`）を検討してください。

参照: libraries-universal-dao.json:s2, libraries-universal-dao.json:s3, libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10