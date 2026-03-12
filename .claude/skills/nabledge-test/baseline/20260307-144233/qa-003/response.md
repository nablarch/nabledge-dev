**結論**: データリードハンドラ（`DataReadHandler`）でファイルを読み込むには、`BatchAction` のサブクラスで `createReader` メソッドをオーバーライドし、`FileDataReader`（またはバリデーション付きの `ValidatableFileDataReader`）のインスタンスを返却する。

**根拠**:

`DataReadHandler`（クラス: `nablarch.fw.handler.DataReadHandler`）は、実行コンテキスト上のデータリーダから入力データを1件ずつ読み込み、後続ハンドラに処理を委譲するハンドラである。

ファイルを読み込む場合は、以下のように `createReader` メソッドをオーバーライドして `FileDataReader` を返却する。

```java
@Override
public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
    // FileDataReader: ファイル読み込み
    return new FileDataReader();
}
```

標準提供のファイル読み込み用データリーダ:

| クラス | 説明 |
|--------|------|
| `nablarch.fw.reader.FileDataReader` | ファイル読み込み |
| `nablarch.fw.reader.ValidatableFileDataReader` | バリデーション機能付きファイル読み込み |
| `nablarch.fw.reader.ResumeDataReader` | レジューム機能付き読み込み（障害回復対応） |

**注意点**:

- `FileDataReader` および `ValidatableFileDataReader` は `data_format` を使用する。`data_bind` を使用する場合はこれらのデータリーダを使用しないこと。
- 標準データリーダで要件を満たせない場合は、`DataReader` インタフェースを実装したカスタムクラスを作成する。
- `DataReadHandler` にはオプションで `maxCount` プロパティを設定でき、最大処理件数を制限できる（例: 大量データを複数日に分けて処理する場合）。

参照: `handlers-data_read_handler.json#overview`, `nablarch-batch-architecture.json#data-readers`, `nablarch-batch-feature_details.json#file-io`
