**結論**: データリードハンドラ（`DataReadHandler`）でファイルを読み込むには、バッチアクションクラスの `createReader` メソッドをオーバーライドして `FileDataReader`（またはバリデーション付きの `ValidatableFileDataReader`）を返却します。

**根拠**:

`DataReadHandler` はデータリーダ（`DataReader`）を使って入力データを1件ずつ読み込み、後続ハンドラに処理を委譲するハンドラです（クラス名: `nablarch.fw.handler.DataReadHandler`）。

ファイルを読み込む場合は、`BatchAction` のサブクラスで `createReader` メソッドをオーバーライドし、`FileDataReader` のインスタンスを返します。

```java
@Override
public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
    // FileDataReader: ファイル読み込み
    return new FileDataReader();
}
```

**標準データリーダの種類**:
- `FileDataReader` (`nablarch.fw.reader.FileDataReader`) — ファイル読み込み
- `ValidatableFileDataReader` (`nablarch.fw.reader.ValidatableFileDataReader`) — バリデーション機能付きファイル読み込み
- `ResumeDataReader` (`nablarch.fw.reader.ResumeDataReader`) — レジューム機能付き読み込み
- `DatabaseRecordReader` (`nablarch.fw.reader.DatabaseRecordReader`) — DB読み込み

**注意点**:
- `FileDataReader` と `ValidatableFileDataReader` は `:ref:`data_format`` を使用します。`:ref:`data_bind`` を使用する場合はこれらのデータリーダを使用しないでください。
- 標準データリーダで要件を満たせない場合は、`DataReader` インタフェースを実装したカスタムクラスを作成してください。
- `DataReadHandler` に `maxCount` プロパティを設定することで、最大処理件数を制限できます（大量データを分割処理する場合に使用）。

参照: `handlers-data_read_handler.json#overview`, `nablarch-batch-architecture.json#data-readers`, `handlers-data_read_handler.json#max-count-setting`
