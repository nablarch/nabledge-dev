# Code Analysis: ImportZipCodeFileAction

**Generated**: 2026-03-13 20:59:11
**Target**: 住所CSVファイルをDBに登録するバッチアクション
**Modules**: nablarch-example-batch
**Analysis Duration**: approx. 4m 0s

---

## Overview

`ImportZipCodeFileAction` は住所CSVファイルを読み込み、1行ずつDBに登録するNablarchバッチアクションクラスである。`BatchAction<ZipCodeForm>` を継承し、`DataReader`（`ZipCodeFileReader`）から渡された住所データをBean Validationで検証した後、`UniversalDao.insert()` でDBに永続化する。バリデーション処理は `@ValidateData` インターセプタに委譲することで、アクション本体をDB登録ロジックのみに集中させている。CSVバインディングには `@Csv`/`@CsvFormat` アノテーションを使用し、データバインド機能（`ObjectMapper`）でCSVを `ZipCodeForm` に自動変換する。

---

## Architecture

### Dependency Graph

```mermaid
classDiagram
    class ImportZipCodeFileAction {
        <<Action>>
    }
    class BatchAction {
        <<Nablarch>>
    }
    class ZipCodeForm {
        <<Form>>
    }
    class ZipCodeFileReader {
        <<DataReader>>
    }
    class ObjectMapperIterator
    class ValidateData {
        <<Interceptor>>
    }
    class ValidateDataImpl {
        <<Nablarch>>
    }
    class ZipCodeData {
        <<Entity>>
    }
    class UniversalDao {
        <<Nablarch>>
    }
    class BeanUtil {
        <<Nablarch>>
    }
    class ObjectMapper {
        <<Nablarch>>
    }
    class ObjectMapperFactory {
        <<Nablarch>>
    }
    class FilePathSetting {
        <<Nablarch>>
    }

    ImportZipCodeFileAction --|> BatchAction : extends
    ImportZipCodeFileAction ..> ZipCodeForm : handles
    ImportZipCodeFileAction ..> ZipCodeFileReader : creates
    ImportZipCodeFileAction ..> BeanUtil : copies
    ImportZipCodeFileAction ..> UniversalDao : inserts
    ImportZipCodeFileAction ..> ZipCodeData : persists
    ValidateData ..> ValidateDataImpl : delegates
    ValidateDataImpl ..> ZipCodeForm : validates
    ZipCodeFileReader ..> ObjectMapperIterator : uses
    ObjectMapperIterator ..> ObjectMapper : wraps
    ZipCodeFileReader ..> ObjectMapperFactory : creates
    ZipCodeFileReader ..> FilePathSetting : resolves
```

**Note**: This diagram uses Mermaid `classDiagram` syntax to show class names and their relationships. Use `--|>` for inheritance (extends/implements) and `..>` for dependencies (uses/creates).

### Component Summary

| Component | Role | Type | Dependencies |
|-----------|------|------|--------------|
| ImportZipCodeFileAction | 住所CSVファイルのDB登録バッチアクション | Action | ZipCodeFileReader, BeanUtil, UniversalDao, ZipCodeData |
| ZipCodeForm | CSVデータのバインド・バリデーション用フォーム | Form | なし（アノテーション定義のみ） |
| ZipCodeFileReader | CSVファイルを1行ずつ読み込むデータリーダ | DataReader | ObjectMapperIterator, ObjectMapperFactory, FilePathSetting |
| ObjectMapperIterator | ObjectMapperをIteratorラップするヘルパー | Utility | ObjectMapper |
| ValidateData | Bean Validationをインターセプトする共通アノテーション | Interceptor | ValidatorUtil, Interceptor |
| ZipCodeData | 住所情報のJPAエンティティ | Entity | なし |

---

## Flow

### Processing Flow

Nablarchバッチフレームワークがハンドラキューを実行する。`DataReadHandler` が `ZipCodeFileReader.read()` を呼び出し、CSVの1行分を `ZipCodeForm` として取得し `ImportZipCodeFileAction.handle()` に渡す。`handle()` メソッドには `@ValidateData` インターセプタが適用されており、`ValidateDataImpl` がBean Validationを実行する。バリデーションエラーの場合はWARNログを出力して処理をスキップし、次のレコードに進む。バリデーション成功時は `BeanUtil.createAndCopy()` で `ZipCodeData` エンティティを生成し、`UniversalDao.insert()` でDBに登録する。`LoopHandler` がデータがなくなるまでこの処理を繰り返し、コミット間隔毎にトランザクションをコミットする。

### Sequence Diagram

```mermaid
sequenceDiagram
    participant Main as nablarch.fw.launcher.Main
    participant DataReadHandler as DataReadHandler<<Nablarch>>
    participant Reader as ZipCodeFileReader
    participant OMIterator as ObjectMapperIterator
    participant Action as ImportZipCodeFileAction
    participant ValidateImpl as ValidateDataImpl<<Nablarch>>
    participant BeanUtil as BeanUtil<<Nablarch>>
    participant DAO as UniversalDao<<Nablarch>>
    participant DB as Database

    Main->>DataReadHandler: execute handler chain
    loop レコードあり
        DataReadHandler->>Reader: read(ctx)
        Reader->>OMIterator: next()
        OMIterator-->>Reader: ZipCodeForm (1行分)
        Reader-->>DataReadHandler: ZipCodeForm

        DataReadHandler->>Action: handle(ZipCodeForm, ctx)
        Note over Action,ValidateImpl: @ValidateData インターセプト
        Action->>ValidateImpl: handle(ZipCodeForm, ctx)
        ValidateImpl->>ValidateImpl: ValidatorUtil.validate(form)
        alt バリデーションエラー
            ValidateImpl->>ValidateImpl: WARN ログ出力
            ValidateImpl-->>Action: null (スキップ)
        else バリデーション成功
            ValidateImpl->>Action: getOriginalHandler().handle(form, ctx)
            Action->>BeanUtil: createAndCopy(ZipCodeData.class, form)
            BeanUtil-->>Action: ZipCodeData
            Action->>DAO: insert(data)
            DAO->>DB: INSERT INTO ZIP_CODE_DATA
            DB-->>DAO: OK
            DAO-->>Action: void
            Action-->>ValidateImpl: Result.Success
            ValidateImpl-->>DataReadHandler: Result.Success
        end
    end
```

---

## Components

### ImportZipCodeFileAction

**ファイル**: [ImportZipCodeFileAction.java](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/action/ImportZipCodeFileAction.java)

**役割**: 住所CSVファイルをDBに登録するバッチアクションの中核クラス。1レコードの処理単位を担当する。

**主要メソッド**:
- `handle(ZipCodeForm, ExecutionContext)` (L35-41): `@ValidateData` インターセプタを経由してバリデーション済みデータを受け取り、`BeanUtil.createAndCopy()` でエンティティ変換後に `UniversalDao.insert()` でDB登録する
- `createReader(ExecutionContext)` (L50-52): `ZipCodeFileReader` のインスタンスを生成して返す

**依存コンポーネント**: ZipCodeFileReader, BeanUtil, UniversalDao, ZipCodeData, ExecutionContext

**実装ポイント**:
- `BatchAction<ZipCodeForm>` を継承することで、フレームワークのバッチ処理ループに組み込まれる
- `@ValidateData` アノテーションでバリデーションロジックをインターセプタに委譲し、ハンドラ本体をDB登録処理に集中させている

---

### ZipCodeForm

**ファイル**: [ZipCodeForm.java](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/form/ZipCodeForm.java)

**役割**: CSVの1行分のデータをバインドし、Bean Validationルールを定義するフォームクラス。

**主要定義**:
- クラスレベルの `@Csv`/`@CsvFormat` (L17-23): CSVフォーマットの宣言（フィールド順、区切り文字、文字コード等）
- 各フィールドの `@Domain`/`@Required` (L30-130): ドメインバリデーションと必須チェック
- `getLineNumber()` (L142-145): `@LineNumber` で行番号を取得（バリデーションエラーログ用）

**依存コンポーネント**: data_bind（`@Csv`, `@CsvFormat`, `@LineNumber`）, bean_validation（`@Domain`, `@Required`）

---

### ZipCodeFileReader

**ファイル**: [ZipCodeFileReader.java](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader/ZipCodeFileReader.java)

**役割**: CSVファイルを `ObjectMapper` で読み込み、1行ずつ `ZipCodeForm` として提供するデータリーダ。

**主要メソッド**:
- `read(ExecutionContext)` (L40-45): イテレータ未初期化時に `initialize()` を呼び出し、`iterator.next()` で1行分のデータを返す
- `hasNext(ExecutionContext)` (L54-59): イテレータの次レコード有無を確認する
- `close(ExecutionContext)` (L68-70): `ObjectMapper` をクローズしリソースを解放する
- `initialize()` (L78-89): `FilePathSetting` でファイルパスを取得し、`ObjectMapperFactory.create()` で `ObjectMapper` を生成してイテレータを初期化する

**依存コンポーネント**: ObjectMapperIterator, ObjectMapperFactory, FilePathSetting

---

### ObjectMapperIterator

**ファイル**: [ObjectMapperIterator.java](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader/iterator/ObjectMapperIterator.java)

**役割**: `ObjectMapper`（`read()`/`null`終端）を `Iterator`（`hasNext()`/`next()`）インタフェースでラップするユーティリティ。`DataReader` 実装をシンプルにするために使用する。

**主要メソッド**:
- コンストラクタ (L32-37): `ObjectMapper` を受け取り、初回データを先読みする
- `hasNext()` (L45-47): `form != null` で次レコードの有無を判定する
- `next()` (L56-60): 現在の `form` を返しつつ次のデータを先読みする
- `close()` (L66-68): `mapper.close()` でリソースを解放する

---

### ValidateData

**ファイル**: [ValidateData.java](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/interceptor/ValidateData.java)

**役割**: `handle()` メソッドをインターセプトし、データレコードに対してBean Validationを実行するカスタムインターセプタ。複数バッチで共通使用できる。

**主要メソッド**:
- `ValidateDataImpl.handle(Object, ExecutionContext)` (L60-92): `ValidatorUtil.getValidator()` でバリデータを取得し、入力データを検証する。エラー時はWARNログを出力して `null` を返す（後続ハンドラをスキップ）。成功時は `getOriginalHandler().handle()` で元の処理に委譲する

**依存コンポーネント**: ValidatorUtil (Nablarch), Interceptor (Nablarch), Logger (Nablarch)

---

## Nablarch Framework Usage

### BatchAction

**クラス**: `nablarch.fw.action.BatchAction`

**説明**: Nablarchバッチフレームワーク用の汎用バッチアクションテンプレートクラス。`handle()` と `createReader()` を実装することでバッチ処理を構築できる。

**使用方法**:
```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {
    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // 1レコード分の業務処理
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

**重要ポイント**:
- ✅ **`handle()` は1レコード単位**: フレームワークが `DataReader` から1件ずつ取得したデータを渡す。ループ処理はフレームワーク（`LoopHandler`）が担当
- 💡 **`DataReader` を自作可能**: `FileDataReader`/`ValidatableFileDataReader` は `data_format` 専用のため、`data_bind` を使う場合は `DataReader` を実装する
- ⚠️ **`FileBatchAction` は使わない**: `data_bind`（`ObjectMapper`）を使う場合は `FileBatchAction` ではなく `BatchAction` を継承すること

**このコードでの使い方**:
- `ImportZipCodeFileAction` が `BatchAction<ZipCodeForm>` を継承（L21）
- `handle()` でバリデーション済みデータのDB登録処理を実装（L35-41）
- `createReader()` で `ZipCodeFileReader` インスタンスを返す（L50-52）

**詳細**: [Nablarch Batch Architecture](../../.claude/skills/nabledge-5/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md)

---

### UniversalDao

**クラス**: `nablarch.common.dao.UniversalDao`

**説明**: JPA 2.0アノテーションを使った簡易O/Rマッパー。SQLを書かずに単純なCRUD操作が可能。

**使用方法**:
```java
// 1件登録
ZipCodeData data = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
UniversalDao.insert(data);
```

**重要ポイント**:
- ✅ **`@Table`, `@Id`, `@Column` が必要**: エンティティクラスにJPAアノテーションを付与しないとCRUD操作できない
- 💡 **SQLなしでCRUD**: エンティティのJPAアノテーション定義だけでINSERT/UPDATE/DELETE/SELECTが実行できる
- ⚠️ **主キー以外の条件更新は不可**: 主キー以外の条件を指定した更新・削除は `UniversalDao` では対応していない。その場合は `database` 機能を使用すること

**このコードでの使い方**:
- `handle()` 内で `UniversalDao.insert(data)` を呼び出してエンティティを1件登録（L38）
- `ZipCodeData` はJPAアノテーション付きエンティティとして定義されている前提

**詳細**: [Libraries Universal_dao](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-universal_dao.md)

---

### ObjectMapper / ObjectMapperFactory

**クラス**: `nablarch.common.databind.ObjectMapper`, `nablarch.common.databind.ObjectMapperFactory`

**説明**: CSVやTSV、固定長データをJava Beansオブジェクトとして読み書きする機能を提供する。フォーマット定義はアノテーションで宣言的に行う。

**使用方法**:
```java
// CSVファイルを読み込む
ObjectMapper<ZipCodeForm> mapper = ObjectMapperFactory.create(
    ZipCodeForm.class, new FileInputStream(zipCodeFile));
ZipCodeForm form;
while ((form = mapper.read()) != null) {
    // 1行分の処理
}
mapper.close();
```

**重要ポイント**:
- ✅ **必ず `close()` を呼ぶ**: `ObjectMapper` はリソースを保持するため、使用後は必ず `close()` を呼び出すこと。`DataReader.close()` で確実にクローズする
- ⚠️ **外部データは全フィールド `String` 型で定義**: CSVなど外部入力は不正値が入る可能性があるため、Java BeansのプロパティはすべてString型で定義すること
- 💡 **アノテーション駆動**: `@Csv`/`@CsvFormat` でフォーマットを宣言的に定義でき、設定ファイルが不要
- ⚡ **スレッドアンセーフ**: 複数スレッドで共有しないこと。バッチでは通常1スレッド1リーダーの構成なので問題なし

**このコードでの使い方**:
- `ZipCodeFileReader.initialize()` で `ObjectMapperFactory.create()` して `ObjectMapper` を生成（L84）
- `ObjectMapperIterator` が `ObjectMapper.read()` を呼び出してデータを取得（L36, L59）
- `ZipCodeFileReader.close()` で `iterator.close()` → `ObjectMapper.close()` が呼ばれる（L69）

**詳細**: [Libraries Data_bind](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-data_bind.md)

---

### Bean Validation（@Csv, @CsvFormat, @Domain, @Required, @LineNumber）

**クラス**: `nablarch.common.databind.csv.Csv`, `nablarch.common.databind.csv.CsvFormat`, `nablarch.core.validation.ee.Domain`, `nablarch.core.validation.ee.Required`, `nablarch.common.databind.LineNumber`

**説明**: `ZipCodeForm` はCSVバインドアノテーションとBean Validationアノテーションを組み合わせて使用している。

**使用方法**:
```java
@Csv(properties = {"localGovernmentCode", "zipCode5digit", ...}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',', ...)
public class ZipCodeForm {
    @Domain("localGovernmentCode")
    @Required
    private String localGovernmentCode;

    @LineNumber
    public Long getLineNumber() { return lineNumber; }
}
```

**重要ポイント**:
- ✅ **`@Csv` の `properties` 順序がCSV列順**: `properties` 配列の順番がCSVの列順と対応する。順番を間違えると誤ったフィールドにデータがバインドされる
- ✅ **`@Required` は `@Domain` と別**: `@Domain` にはドメインのバリデーションルールのみ定義し、`@Required` は必要な各フィールドに個別に設定する
- 💡 **`@LineNumber` でエラー行番号取得**: バリデーションエラー時にCSVの行番号をログ出力できる。`ValidateData` インターセプタが `getLineNumber()` でこの値を取得する

**このコードでの使い方**:
- `ZipCodeForm` クラスに `@Csv`/`@CsvFormat` を付与してCSVフォーマットを定義（L17-23）
- 全15フィールドに `@Domain`/`@Required` でバリデーションルールを定義（L30-130）
- `getLineNumber()` に `@LineNumber` を付与してバリデーションエラー時の行番号ログを有効化（L142-145）

**詳細**: [Libraries Bean_validation](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-bean_validation.md), [Libraries Data_bind](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-data_bind.md)

---

### ValidatorUtil（インターセプタでの明示的バリデーション）

**クラス**: `nablarch.core.validation.ee.ValidatorUtil`

**説明**: Bean Validationを明示的に実行するユーティリティ。`ValidateData` インターセプタがバッチ入力データのバリデーションに使用する。

**使用方法**:
```java
// インターセプタ内でのバリデーション実行
Validator validator = ValidatorUtil.getValidator();
Set<ConstraintViolation<Object>> violations = validator.validate(data);
if (violations.isEmpty()) {
    return getOriginalHandler().handle(data, context);
}
// エラー時はWARNログ出力してnullを返す
```

**重要ポイント**:
- 💡 **インターセプタで共通化**: バリデーションロジックをインターセプタに切り出すことで、複数のバッチアクションで共通使用できる
- ⚠️ **エラー時は `null` を返す**: バリデーションエラーレコードはスキップ（`null` 返却）してバッチ処理を継続させる設計。このため `handle()` の戻り値が `null` の場合は後続処理が実行されない
- ✅ **行番号のログ出力**: `BeanUtil.getProperty(data, "lineNumber")` で行番号を取得し、エラーメッセージに含めることで問題レコードの特定が容易になる

**このコードでの使い方**:
- `ValidateDataImpl.handle()` で `ValidatorUtil.getValidator()` を使い、受け取ったフォームデータをバリデーション（L63-64）
- バリデーションエラー時は行番号をWARNログに出力（L82-90）
- バリデーション成功時のみ `getOriginalHandler().handle()` で `ImportZipCodeFileAction.handle()` を呼び出す（L68）

**詳細**: [Libraries Bean_validation](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-bean_validation.md)

---

## References

### Source Files

- [ImportZipCodeFileAction.java (v5)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/action/ImportZipCodeFileAction.java)
- [ZipCodeForm.java (v5)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/form/ZipCodeForm.java)
- [ZipCodeFileReader.java (v5)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader/ZipCodeFileReader.java)
- [ObjectMapperIterator.java (v5)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader/iterator/ObjectMapperIterator.java)
- [ValidateData.java (v5)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/interceptor/ValidateData.java)

### Knowledge Base (Nabledge-5)

- [Nablarch Batch Getting Started Nablarch Batch](../../.claude/skills/nabledge-5/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md)
- [Nablarch Batch Architecture](../../.claude/skills/nabledge-5/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md)
- [Libraries Universal_dao](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-universal_dao.md)
- [Libraries Data_bind](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-data_bind.md)
- [Libraries Bean_validation](../../.claude/skills/nabledge-5/docs/component/libraries/libraries-bean_validation.md)

### Official Documentation

- [BatchAction](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/action/BatchAction.html)
- [UniversalDao](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/common/dao/UniversalDao.html)
- [ObjectMapper](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/common/databind/ObjectMapper.html)
- [ObjectMapperFactory](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/common/databind/ObjectMapperFactory.html)
- [BeanUtil](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/core/beans/BeanUtil.html)
- [LineNumber](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/common/databind/LineNumber.html)
- [ValidatorUtil](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/core/validation/ee/ValidatorUtil.html)
- [DataReader](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/DataReader.html)
- [Data Bind](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/libraries/data_io/data_bind.html)
- [Universal Dao](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/libraries/database/universal_dao.html)
- [Bean Validation](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/libraries/validation/bean_validation.html)
- [Architecture](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/batch/nablarch_batch/architecture.html)
- [Index](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/batch/nablarch_batch/getting_started/nablarch_batch/index.html)

---

**Note**: This documentation was generated by the code-analysis workflow of the nabledge-5 skill.