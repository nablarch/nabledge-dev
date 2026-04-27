# Code Analysis: ImportZipCodeFileAction

コード解析ドキュメントを生成しました。

**Output**: `/home/tie303177/work/nabledge/work2/.nabledge/20260424/code-analysis-ImportZipCodeFileAction.md`
**Analysis Duration**: approx. 2m 22s

## Overview

`ImportZipCodeFileAction` は、Nablarch の `BatchAction` を継承した業務アクションクラスで、日本郵便が提供する住所ファイル（CSV）を1行ずつ読み込み、データベースの住所エンティティテーブルに登録するバッチ処理を実装しています。データリーダ(`ZipCodeFileReader`) が CSV ファイルを `ZipCodeForm` にバインドして行単位で渡し、`@ValidateData` インターセプタによる Bean Validation を経由した後、`UniversalDao#insert` で DB に登録する、Nablarch の典型的な「ファイル to DB」バッチパターンです。

## Architecture (主要クラス)

| Component | Role | Type | Dependencies |
|-----------|------|------|--------------|
| ImportZipCodeFileAction | 住所ファイル登録バッチアクション | Action (BatchAction) | ZipCodeForm, ZipCodeFileReader, ZipCodeData, UniversalDao, BeanUtil, ValidateData |
| ZipCodeForm | 住所1行分をバインドする CSV フォーム | Form (Bean) | @Domain, @Required |
| ZipCodeFileReader | 住所 CSV を1行ずつ読むデータリーダ | DataReader | ObjectMapperFactory, FilePathSetting, ObjectMapperIterator |
| ValidateData (ValidateDataImpl) | Bean Validation を共通化するインターセプタ | Interceptor | ValidatorUtil, BeanUtil, MessageUtil, Logger |
| ZipCodeData | DB 登録用の住所エンティティ | Entity | なし |

## Flow (要点)

1. フレームワークが `createReader(ctx)` で `ZipCodeFileReader` を取得。
2. Reader 初回 `hasNext`/`read` で `FilePathSetting#getFileWithoutCreate("csv-input","importZipCode")` によりファイル解決、`ObjectMapperFactory.create(ZipCodeForm.class, FileInputStream)` からイテレータ生成。
3. 各行 `read()` が `ZipCodeForm` にバインド（`@LineNumber` で行番号自動設定）。
4. `handle` 呼び出し時に `@ValidateData` → `ValidateDataImpl#handle` が起動。違反時は `lineNumber` 付き WARN ログで後続スキップ。
5. 違反なし時のみ `ImportZipCodeFileAction#handle` が `BeanUtil.createAndCopy(ZipCodeData.class, inputData)` → `UniversalDao.insert(data)` で登録、`Result.Success` を返却。
6. 全件終了後、Reader の `close(ctx)` でストリーム解放。

## Nablarch Framework Usage (抜粋)

- **BatchAction**: `createReader` と `handle` を実装する、ファイル to DB 型バッチの基底クラス。ループとトランザクション境界はフレームワーク側。
- **DataReader / ObjectMapperFactory**: `@Csv`/`@CsvFormat` と `@LineNumber` によるアノテーション駆動の CSV バインド。`hasNext`/`read`/`close` を実装。
- **@ValidateData / ValidatorUtil**: Jakarta Bean Validation を Nablarch バッチのハンドラ前段で共通化するメソッドインターセプタ。違反時は WARN ログ＋スキップ。
- **UniversalDao + BeanUtil**: `BeanUtil.createAndCopy` で Form → Entity 変換、`UniversalDao.insert(entity)` で INSERT。トランザクションはハンドラキュー側。
- **FilePathSetting**: 論理名（`csv-input`）から物理ファイルパスを解決し、環境差分を設定で吸収。

## References

- Source: `.lw/nab-official/v6/nablarch-example-batch/...` (ImportZipCodeFileAction / ZipCodeForm / ZipCodeFileReader / ValidateData)
- Knowledge: Nablarch Batch Getting Started / Libraries Data Bind / Bean Validation / Universal Dao
