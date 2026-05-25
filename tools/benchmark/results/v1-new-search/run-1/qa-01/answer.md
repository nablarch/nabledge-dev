**結論**: Nablarchバッチで大量データを1件ずつ処理するには、`createReader`メソッドで`DatabaseRecordReader`（または`DataReader`実装クラス）を使い、フレームワークのデータリーダ機構に任せる。これがNablarchバッチの正しい設計であり、フレームワークが1件ずつ`handle`を呼び出すため、全件をメモリに展開しない。

**根拠**:

**方法1: DatabaseRecordReaderをcreateReaderで使う（推奨）**

Nablarchバッチの処理の流れは次のとおり：

1. `DataReader`が入力データを読み込み、**データレコードを1件ずつ**提供する
2. `handle`メソッドが1件分のデータに対して業務ロジックを実行する
3. 処理対象データがなくなるまで繰り返す

DBからデータを読み込む場合は、標準提供の `DatabaseRecordReader` を `createReader` で設定する。

```java
@Override
public DataReader<SqlRow> createReader(ExecutionContext ctx) {
    DatabaseRecordReader reader = new DatabaseRecordReader();
    // SQLを設定（全件SELECT）
    reader.setStatement(statement);
    return reader;
}

@Override
public Result handle(SqlRow inputData, ExecutionContext ctx) {
    // 1件分の処理のみ行う
    // ...
    return new Result.Success();
}
```

**アンチパターン（避けること）**:

`handle`内でSELECTを発行して自前ループするのは典型的な誤りで、大量データ時に問題が発生する：

```java
// NG: handleでSELECTして自前ループ
public Result handle(ExecutionContext context) {
    SqlResultSet sqlResultSet = search("SEARCH");
    for (SqlRow row : sqlResultSet) {
        // 更新処理
    }
}
```

この実装の問題：
- 検索結果を全件メモリに展開する → メモリ不足になる
- フレームワークのコミット間隔制御が機能しない → トランザクションログを逼迫する

解決法：`handle`内で発行しているSQLを`createReader`で行うようにする。

**方法2: ユニバーサルDAO遅延ロード**

`DatabaseRecordReader`ではなく`UniversalDao`を使う場合は、`UniversalDao#defer`メソッドを使って遅延ロードする：

```java
// try-with-resourcesを使ったclose呼び出し。
// DeferredEntityListはダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

遅延ロードはユニバーサルDAOとしては1件ずつロードする。内部でサーバサイドカーソルを使用しているため、`DeferredEntityList#close`の呼び出しが必要（try-with-resourcesで自動close推奨）。

**注意点**:
- 遅延ロード（`UniversalDao#defer`）使用時は、**カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる**場合がある。使用するRDBMSによって異なるため、データベースベンダーのマニュアルを確認すること。問題がある場合はページングなどで回避する。
- `DatabaseRecordReader`を`createReader`で使う方法がNablarchバッチの基本設計であり、こちらを優先的に検討すること。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s7, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s10, nablarch-patterns-Nablarchアンチパターン.json:s11, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, libraries-universal-dao.json:s9

---