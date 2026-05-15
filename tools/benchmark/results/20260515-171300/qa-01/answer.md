**結論**: 大量データを1件ずつ読み込むには、UniversalDAO の「遅延ロード」機能（`UniversalDao#defer()`）を使用します。

**根拠**:

`UniversalDao.defer()` を検索前に呼び出すだけで遅延ロードが有効になり、内部でサーバサイドカーソルを使用して1件ずつロードします。`DeferredEntityList` は `Closeable` なので try-with-resources で確実にクローズしてください。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

メモリ使用量はJDBCのフェッチサイズによって変動します（詳細はデータベースベンダーのマニュアルを参照）。

**Jakarta Batch（Doma使用）の場合**:

DomaアダプタでJakarta Batchを使う場合は、DaoインタフェースでStreamを返すメソッドを定義し、`DomaDaoRepository#get(Class, Class)` の第2引数に `DomaTransactionNotSupportedConfig.class` を指定します。

```java
// Daoインタフェース
@Select(strategy = SelectType.RETURN)
Stream<Project> search();

// ItemReader
final ProjectDao dao = DomaDaoRepository.get(ProjectDao.class, DomaTransactionNotSupportedConfig.class);
stream = dao.search();
iterator = stream.iterator();
```

**注意点**:

- カーソルオープン中にトランザクション制御を行うと、RDBMSによってはカーソルがクローズされエラーになる場合があります。トランザクション制御が必要な場合は、ページング（`UniversalDao.per().page()`）での回避を検討してください。
- Jakarta Batch + Domaの場合、引数1つの `DomaDaoRepository#get(Class)` を使うと `DomaConfig` が適用され、トランザクションコミット時にストリームがクローズされて後続レコードが読めなくなります。必ず2引数版を使用してください。

参照: `component/libraries/libraries-universal-dao.json#s9`, `component/adapters/adapters-doma-adaptor.json#s10`