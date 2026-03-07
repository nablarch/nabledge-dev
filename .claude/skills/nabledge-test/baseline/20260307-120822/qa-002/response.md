**結論**: UniversalDaoでページングを実装するには、`UniversalDao.per(件数).page(ページ番号)` を検索メソッドの前に呼び出します。

**根拠**:

`UniversalDao#per` と `UniversalDao#page` を検索前に呼び出してページングを実行します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

- `per(3)` : 1ページあたりの件数を3件に設定
- `page(1)` : 取得するページ番号（1始まり）を指定

**ページング情報の取得**: `EntityList` から `Pagination` オブジェクトを取得できます。

```java
Pagination pagination = users.getPagination();
```

`Pagination` オブジェクトには総件数・総ページ数・現在ページなどのページング情報が含まれます。

**前提設定**: UniversalDaoを使用するには、`database` の設定に加えて `BasicDaoContextFactory` をコンポーネント定義に追加する必要があります。

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

コンポーネント名は `daoContextFactory` 固定です。

**注意点**:

- ページング処理ではレコード取得の前に件数取得SQL（`SELECT COUNT(*) FROM (...)`）が自動的に発行されます。元SQLに `ORDER BY` 句が含まれる場合、件数取得時に不要な処理負荷が発生することがあります。
- 性能が問題になる場合は、ダイアレクトをカスタマイズして `Dialect#convertCountSql` の実装を変更し、専用の件数取得SQLを使用できます。
- ページングは `findAllBySqlFile` と組み合わせて使用します（SQLファイルのパスはBeanのFQCNから導出されます）。
- 大量データ処理の場合、ページングの代替として遅延ロード（`UniversalDao.defer()`）も利用できますが、カーソル管理が必要になります。

参照: `libraries-universal_dao.json#paging`, `libraries-universal_dao.json#extension-examples`, `libraries-universal_dao.json#setup`, `libraries-universal_dao.json#sql-file-search`
