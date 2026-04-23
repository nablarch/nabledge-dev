**結論**: UniversalDaoでページング検索を実装するには、検索メソッド呼び出しの前に `UniversalDao#per` メソッドと `UniversalDao#page` メソッドをチェーンで呼び出すだけで実現できます。ページング表示に必要な情報（総件数など）は、検索結果の `EntityList` から取得できる `Pagination` オブジェクトが保持します。

**根拠**:

基本的な実装例（`libraries-universal-dao.json#s12`）:

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

- `per(n)`: 1ページあたりの件数を指定（例: 3件）
- `page(n)`: 取得するページ番号を指定（例: 1ページ目）
- その後に通常の検索メソッド（`findAllBySqlFile` など）を呼び出す

ページング表示用の情報取得:

```java
Pagination pagination = users.getPagination();
```

`Pagination` は `EntityList#getPagination()` から取得でき、画面表示に必要な検索結果件数などの情報を保持します。

**注意点**:

- ページングでは、実際の範囲指定レコードの取得処理の前に **件数取得SQL** が発行されます（デフォルトでは元のSQLを `SELECT COUNT(*) FROM` で包んだSQL）。
- 元のSQLが `ORDER BY` 句を含むなど処理負荷が大きい場合、件数取得SQLが性能劣化の原因となることがあります。その場合は、使用しているダイアレクトを継承して `Dialect#convertCountSql(String, Object, StatementFactory)` をカスタマイズし、件数取得SQLを変更することで対応します（`libraries-universal-dao.json#s23`）。
- **重要**: 件数取得SQLを変更する場合、元のSQLと同一の検索条件を保つ必要があります（両者の検索条件に差分が発生しないよう注意）。
- ページング用の検索処理の低レベル実装には、データベースアクセス(JDBCラッパー)の範囲指定検索機能が使用されます。

参照:
- `component/libraries/libraries-universal-dao.json#s12` (ページングを行う)
- `component/libraries/libraries-universal-dao.json#s23` (ページング処理の件数取得用SQLを変更する)
