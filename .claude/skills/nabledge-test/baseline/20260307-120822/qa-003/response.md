**結論**: データリードハンドラ（DataReadHandler）でファイルを読み込むには、BatchActionの`createReader`メソッドをオーバーライドし、`FileDataReader`（または`ValidatableFileDataReader`）を返却するように実装します。

**根拠**:

DataReadHandlerは、BatchActionのサブクラスで`createReader`メソッドをオーバーライドすることで使用するDataReaderを指定します。

```java
@Override
public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
    // FileDataReader: ファイル読み込み
    return new FileDataReader();
}
```

ファイル読み込み用の標準データリーダ:

- `FileDataReader` (`nablarch.fw.reader.FileDataReader`) — ファイル読み込み
- `ValidatableFileDataReader` (`nablarch.fw.reader.ValidatableFileDataReader`) — バリデーション機能付きファイル読み込み
- `ResumeDataReader` (`nablarch.fw.reader.ResumeDataReader`) — レジューム機能付き読み込み（障害回復対応）

DataReadHandlerの処理の流れ:
1. データリーダを使用して入力データを1件ずつ読み込む
2. 実行時IDを採番する
3. データ終端に達した場合、`NoMoreRecord`を返却して処理を終了する

**注意点**:
- `FileDataReader`と`ValidatableFileDataReader`はデータフォーマット定義（`data_format`）を使用する。データバインド（`data_bind`）を使用する場合は、これらのデータリーダを使用しないこと。
- DataReadHandlerより手前のハンドラで`ExecutionContext`に`DataReader`が設定されている必要がある。`DataReader`が未設定の場合、処理対象データ無しとして`NoMoreRecord`を返却し処理を終了する。
- 標準データリーダで要件を満たせない場合は、`DataReader`インタフェースを実装したカスタムクラスを作成する。

参照: `component/handlers/handlers-data_read_handler.json#overview`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#data-readers`
