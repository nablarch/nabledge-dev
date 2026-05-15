**結論**: 大量データを1件ずつ読み込むには、ユニバーサルDAOの**遅延ロード**機能（`UniversalDao#defer()`）を使用する。

**根拠**:

ユニバーサルDAOでは、`UniversalDao#defer()` メソッドを事前に呼び出すことで遅延ロードが有効になる。内部でサーバサイドカーソルを使用し、すべての検索結果を一度にメモリに展開せずに1件ずつ処理できる。

```java
// try-with-resources を使った close 呼び出し。
// DeferredEntityList はダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // user を使った処理
    }
}
```

ポイント：
- `UniversalDao#defer()` を検索前に呼び出すだけで遅延ロードが有効になる
- 戻り値を `DeferredEntityList<T>` にダウンキャストして取得する
- `DeferredEntityList` は `AutoCloseable` を実装しているため、**`try-with-resources` で必ず `close()` を呼び出す**
- メモリ使用量はJDBCのフェッチサイズに依存する（詳細はDBベンダーのマニュアルを参照）

**注意点**:

- **トランザクション制御に注意**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる。遅延ロード中にトランザクション制御を行うと、クローズ済みカーソルを参照してエラーになる場合がある。
- 回避策として、DBベンダーのマニュアルに沿ってカーソルの挙動を調整するか、大量データを扱わないようページング（`UniversalDao#per()`, `UniversalDao#page()`）で対処する方法もある。
- **Jakarta Batchでの使用（Domaアダプター利用時）**: Domaアダプターを使っている場合は `DomaDaoRepository#get(Class, Class)` の第2引数に `DomaTransactionNotSupportedConfig` を指定し、Daoの戻り値を `Stream<T>` で受け取る実装が必要。引数1つの `DomaDaoRepository#get(Class)` を使うと、トランザクションのコミット時にストリームがクローズされて後続レコードが読めなくなる。

参照: `component/libraries/libraries-universal-dao.json#s9`, `component/adapters/adapters-doma-adaptor.json#s10`