読み取ったセクション内容から回答を生成します。

**結論**: UniversalDaoでデータを検索するには、主に `UniversalDao.findAllBySqlFile()` メソッドにBeanクラスとSQL IDを指定する方法を使う。条件を渡す場合は第3引数に検索条件Beanを指定する。

**根拠**:

**1. 事前設定**

コンポーネント定義に `BasicDaoContextFactory` を追加する。

```xml
<!-- コンポーネント名は"daoContextFactory"で設定する。 -->
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

**2. SQLファイルを使った検索**

SQLファイルを作成し、SQL IDを指定して検索する。検索結果はBeanにマッピングされる（Beanのプロパティ名とSELECT句の名前が一致する項目をマッピング）。

```java
// 全件検索
UniversalDao.findAllBySqlFile(User.class, "FIND_BY_NAME");
```

SQLファイルのパスはBeanクラスから導出される。例えば `sample.entity.User` の場合、クラスパス配下の `sample/entity/User.sql` となる。

**3. 条件を指定した検索**

```java
// 検索条件を取得する
ProjectSearchForm condition = context.getRequestScopedVar("form");

// 条件を指定して検索する
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

検索条件は、Entityではなく検索条件を持つ専用のBeanを指定する（1テーブルのみへのアクセスの場合はEntityでも可）。

**4. 大量データの遅延ロード**

バッチ処理などで大量データを扱う場合は `UniversalDao#defer` メソッドを使う。内部でサーバサイドカーソルを使用するため `DeferredEntityList#close` が必要。

```java
// try-with-resourcesを使ったclose呼び出し。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**注意点**:
- 遅延ロード中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる場合がある。データベースベンダのマニュアルを確認するか、ページングで回避すること。
- 複数テーブルをJOINする場合は、個別に検索せず1回で検索できるSQLとマッピング用Beanを作成すること。

参照: libraries-universal-dao.json:s6, libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s9

---