### Answer

Nablarchバッチで大量データを1件ずつ読み込む方法は、主に以下の2つです。

---

## 1. DataReaderを使ったフレームワーク標準の仕組み（推奨）

Nablarchバッチは、`createReader`メソッドで返した`DataReader`が**1件ずつデータを提供**し、アクションクラスの`handle`メソッドが1件ずつ処理するアーキテクチャになっています。

```
DataReader → 1件取得 → handle処理 → 1件取得 → handle処理 → ... （処理対象データがなくなるまで繰り返す）
```

標準で提供されているデータリーダ：

| データリーダ | 用途 |
|---|---|
| `DatabaseRecordReader` | データベースから読み込み |
| `FileDataReader` | ファイルから読み込み |
| `ValidatableFileDataReader` | バリデーション付きファイル読み込み |
| `ResumeDataReader` | レジューム機能付き読み込み |

**重要なアンチパターン：** `handle`メソッド内で自前ループを書くのは誤りです。

```java
// NG: NoInputDataBatchAction を使って自前でループ処理
public Result handle(ExecutionContext context) {
    SqlResultSet sqlResultSet = search("SEARCH"); // 全件メモリ展開
    for (SqlRow row : sqlResultSet) {             // 自前ループ ← アンチパターン
        // 更新処理
    }
}
```

これは大量件数を処理できず、フレームワークのコミット間隔制御なども効きません。

---

## 2. UniversalDAOの遅延ロード（defer）

`DatabaseRecordReader`の代わりに UniversalDAO の遅延ロードを使う方法もあります。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

`UniversalDao.defer()` を先に呼ぶだけで遅延ロードが有効になり、内部でサーバサイドカーソルを使用して1件ずつロードします。メモリ使用量はJDBCのフェッチサイズに依存します。

**注意点：** RDBMSによっては、カーソルオープン中にトランザクション制御（コミット等）を行うとカーソルがクローズされエラーになる場合があります。データベースベンダーのマニュアルを確認してください。

---

## 3. 処理件数を分割して実行する方法（補足）

`DataReadHandler` の `maxCount` を設定することで、1回のバッチ実行の処理件数を制限できます。

```xml
<component class="nablarch.fw.handler.DataReadHandler">
  <!-- 1回の実行で最大1万件のみ処理 -->
  <property name="maxCount" value="10000" />
</component>
```

これにより、例えば総件数100万件のバッチを日次10万件ずつ10日間に分けて処理させることができます。

---

**まとめ：** 大量データ処理の基本は `createReader` で `DataReader` を返し、フレームワークに1件ずつの処理を任せることです。`handle`内での全件取得・自前ループはN+1問題やメモリ枯渇の典型的なアンチパターンです。