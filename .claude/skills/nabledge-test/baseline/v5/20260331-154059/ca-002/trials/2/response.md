`ImportZipCodeFileAction` は、住所（郵便番号）CSVファイルをDBに登録するNablarchバッチアクションクラスである。`BatchAction<ZipCodeForm>` を継承し、CSVファイルから1行ずつ読み込んだデータをバリデーションしてDBに登録する。

主要コンポーネントは以下の3つで構成される:
- **ImportZipCodeFileAction**: バッチアクション本体。`handle()` でDB登録、`createReader()` でデータリーダを生成する
- **ZipCodeFileReader**: CSVファイル読み込み用のカスタムデータリーダ。`ObjectMapperFactory` と `ObjectMapperIterator` を組み合わせてファイルを1行ずつ提供する
- **ZipCodeForm**: CSVバインディングとBean Validationを兼ねるフォームクラス。`@Csv`/`@CsvFormat` でCSVフォーマットを定義し、`@Domain`/`@Required` でバリデーションルールを定義する

バリデーションは `@ValidateData` インターセプタで自動実行され、エラー時はWARNログを出力してそのレコードをスキップする。

詳細なコード分析ドキュメントは `.nabledge/20260331/code-analysis-ImportZipCodeFileAction.md` に出力されました。

---

**アーキテクチャ概要**

```
BatchAction (Nablarch)
    ^
    | extends
ImportZipCodeFileAction
    |-- creates --> ZipCodeFileReader (DataReader)
    |                   |-- delegates --> ObjectMapperIterator
    |                   |                     |-- wraps --> ObjectMapper (Nablarch data_bind)
    |                   |-- resolves --> FilePathSetting (Nablarch)
    |-- receives --> ZipCodeForm (CSV binding + Bean Validation)
    |-- intercepted by --> @ValidateData --> ValidatorUtil (Nablarch)
    |-- copies via --> BeanUtil (Nablarch)
    |-- persists via --> UniversalDao.insert() (Nablarch)
    |-- creates --> ZipCodeData (Entity)
```

**処理フロー要約**

1. ハンドラキューが `DataReadHandler` 経由で `ZipCodeFileReader.read()` を呼び出し
2. `ZipCodeFileReader` が `ObjectMapperFactory` でCSVをバインドして `ZipCodeForm` を提供
3. `@ValidateData` インターセプタが Bean Validation を実行 → エラー時はスキップ、成功時は `handle()` を呼び出し
4. `handle()` で `BeanUtil.createAndCopy` → `UniversalDao.insert` を実行してDB登録
5. `hasNext() == false` でループ終了、`close()` でストリーム解放

**Nablarchフレームワーク利用箇所**

| クラス | 用途 | 重要ポイント |
|--------|------|------|
| `BatchAction` | バッチアクション基底クラス | data_bindを使う場合はFileBatchActionではなくBatchActionを使う |
| `UniversalDao.insert()` | DB登録 | 大量データ時はbatchInsertを検討 |
| `ObjectMapperFactory` | CSVバインド | 必ずclose()を呼ぶ |
| `BeanUtil.createAndCopy()` | フォーム→エンティティコピー | 同名プロパティのみコピー |
| `ValidatorUtil.getValidator()` | Bean Validation実行 | @ValidateDataインターセプタ経由 |