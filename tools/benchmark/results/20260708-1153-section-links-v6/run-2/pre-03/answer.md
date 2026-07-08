**結論**: UniversalDaoでデータベースデータを検索するには、SQLファイルを作成して`UniversalDao.findAllBySqlFile()`メソッドにSQL IDを指定するのが基本です。条件指定の検索も同メソッドの第3引数に検索条件Beanを渡すことで対応できます。

**根拠**:

**事前設定**

コンポーネント定義ファイルに`BasicDaoContextFactory`を追加します（データベースアクセス(JDBCラッパー)の設定も別途必要）:

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**任意のSQLで検索する場合**

SQLファイルを作成し、SQL IDを指定して検索します:

```java
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスは、マッピング先のBeanクラスから導出されます。例えば`sample.entity.User`クラスの場合、クラスパス配下の`sample/entity/User.sql`がSQLファイルのパスになります。

**条件を指定して検索する場合**

検索条件を持つBeanを第3引数に指定します:

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件はEntityではなく専用の条件Beanを指定することが推奨されています（1テーブルのみへのアクセスの場合はEntityでも可）。

検索結果は、BeanのプロパティとSELECT句の名前が一致する項目に自動的にマッピングされます。

**注意点**:
- 大量データを扱う場合（バッチ処理・大量ダウンロードなど）は`UniversalDao.defer()`による遅延ロードを使用し、`try-with-resources`で`DeferredEntityList#close()`を確実に呼び出してください:

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

- 使用するRDBMSによっては、遅延ロード中にトランザクション制御を行うとカーソルがクローズされエラーとなる場合があります。

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  任意のSQL(SQLファイル)で検索する
  条件を指定して検索する
  検索結果をBeanにマッピングできる
  ユニバーサルDAOを使うための設定を行う
  検索結果を遅延ロードする