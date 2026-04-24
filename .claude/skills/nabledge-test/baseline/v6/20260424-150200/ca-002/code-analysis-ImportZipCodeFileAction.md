# Code Analysis: ImportZipCodeFileAction

**Generated**: 2026-04-24 15:03:36
**Target**: 住所ファイル（CSV）を読み込んでデータベースに登録するバッチアクション
**Modules**: nablarch-example-batch
**Analysis Duration**: unknown

---

## Overview

`ImportZipCodeFileAction` は Nablarch バッチ（`BatchAction`）として実装された、住所情報CSVファイルを1行ずつ読み込み `ZIP_CODE` テーブルへ登録する業務アクションである。`ZipCodeFileReader` が `ObjectMapper` を利用して CSV を `ZipCodeForm` にバインドし、`@ValidateData` インターセプタが Bean Validation を実行後、`handle` メソッドが `BeanUtil.createAndCopy` で `ZipCodeData` エンティティに詰め替え、`UniversalDao.insert` で DB 登録する構造になっている。

---

## Architecture

### Dependency Graph

```mermaid
classDiagram
    class ImportZipCodeFileAction
    class ZipCodeForm
    class ZipCodeFileReader
    class ValidateData
    class ValidateDataImpl
    class ZipCodeData
    class BatchAction {
        <<Nablarch>>
    }
    class DataReader {
        <<Nablarch>>
    }
    class UniversalDao {
        <<Nablarch>>
    }
    class BeanUtil {
        <<Nablarch>>
    }
    class ObjectMapperFactory {
        <<Nablarch>>
    }
    class FilePathSetting {
        <<Nablarch>>
    }
    class Interceptor {
        <<Nablarch>>
    }
    class ValidatorUtil {
        <<Nablarch>>
    }

    ImportZipCodeFileAction --|> BatchAction : extends
    ImportZipCodeFileAction ..> ZipCodeForm : handles
    ImportZipCodeFileAction ..> ZipCodeData : creates
    ImportZipCodeFileAction ..> ZipCodeFileReader : creates
    ImportZipCodeFileAction ..> BeanUtil : copies via
    ImportZipCodeFileAction ..> UniversalDao : persists via
    ImportZipCodeFileAction ..> ValidateData : annotated with
    ZipCodeFileReader ..|> DataReader : implements
    ZipCodeFileReader ..> ZipCodeForm : reads
    ZipCodeFileReader ..> ObjectMapperFactory : creates mapper via
    ZipCodeFileReader ..> FilePathSetting : resolves path via
    ValidateData ..> Interceptor : declares
    ValidateDataImpl ..> ValidatorUtil : validates via
    ValidateData +-- ValidateDataImpl
```

**Note**: This diagram uses Mermaid `classDiagram` syntax to show class names and their relationships. Use `--|>` for inheritance (extends/implements) and `..>` for dependencies (uses/creates).

### Component Summary

| Component | Role | Type | Dependencies |
|-----------|------|------|--------------|
| ImportZipCodeFileAction | 1行分の住所データをDBへ登録する業務アクション | Action (BatchAction) | ZipCodeForm, ZipCodeFileReader, ZipCodeData, UniversalDao, BeanUtil, @ValidateData |
| ZipCodeForm | CSVレコードをバインドし Bean Validation するフォーム | Form | @Csv / @CsvFormat / @Required / @Domain / @LineNumber |
| ZipCodeFileReader | CSV を1行ずつ ZipCodeForm として返却するデータリーダ | DataReader | ObjectMapperFactory, FilePathSetting, ObjectMapperIterator |
| ValidateData | ハンドラ実行前に Bean Validation を実行するインターセプタ | Interceptor (annotation) | Interceptor, ValidatorUtil, BeanUtil, MessageUtil |
| ZipCodeData | DB 登録対象の Entity | Entity (JPA) | （UniversalDao 用の @Entity クラス） |

---

## Flow

### Processing Flow

1. Nablarch バッチ基盤が `ImportZipCodeFileAction#createReader` (Line 48-51) を呼び出し、`ZipCodeFileReader` を生成する。
2. `ZipCodeFileReader#read` が初回呼び出しで `initialize()` を実行し、`FilePathSetting.getInstance().getFileWithoutCreate("csv-input", "importZipCode")` でファイルを解決、`ObjectMapperFactory.create(ZipCodeForm.class, FileInputStream)` で `ObjectMapper` を生成、`ObjectMapperIterator` でラップする。
3. バッチ基盤は 1 行ずつ `read` を呼び出し、`ZipCodeForm` を取得する（`hasNext` が `false` になるまでループ）。
4. 取得した `ZipCodeForm` を引数に `ImportZipCodeFileAction#handle` が呼ばれるが、実行前に `@ValidateData` インターセプタ（`ValidateData.ValidateDataImpl#handle`）がフックされ、`ValidatorUtil.getValidator().validate(data)` で Bean Validation を実行する。
5. バリデーションエラーがある場合は `MessageUtil.createMessage(WARN, "invalid_data_record", ...)` で行番号付きの警告ログを出し、本体の `handle` は呼ばない（`return null`）。エラーが無ければ `getOriginalHandler().handle(data, context)` で本体を実行する。
6. `ImportZipCodeFileAction#handle` (Line 34-41) は `BeanUtil.createAndCopy(ZipCodeData.class, inputData)` で Form → Entity へプロパティをコピーし、`UniversalDao.insert(data)` でテーブルへ登録、`Result.Success` を返却する。
7. 全行読み終えた後、基盤が `ZipCodeFileReader#close` を呼び、`ObjectMapperIterator#close()` でストリームを解放する。

### Sequence Diagram

```mermaid
sequenceDiagram
    participant Batch as Nablarch Batch Runtime
    participant Action as ImportZipCodeFileAction
    participant Reader as ZipCodeFileReader
    participant Mapper as ObjectMapper&lt;ZipCodeForm&gt;
    participant Interceptor as ValidateDataImpl
    participant Validator as ValidatorUtil
    participant BeanUtil as BeanUtil
    participant Dao as UniversalDao
    participant DB as Database

    Batch->>Action: createReader(ctx)
    Action-->>Batch: new ZipCodeFileReader()

    loop 各行
        Batch->>Reader: hasNext(ctx)
        Reader->>Reader: initialize() (初回のみ)
        Note over Reader: FilePathSetting.getFileWithoutCreate("csv-input","importZipCode")<br/>ObjectMapperFactory.create(ZipCodeForm.class, FileInputStream)
        Reader-->>Batch: true/false
        Batch->>Reader: read(ctx)
        Reader->>Mapper: next()
        Mapper-->>Reader: ZipCodeForm
        Reader-->>Batch: ZipCodeForm

        Batch->>Interceptor: handle(form, ctx)
        Interceptor->>Validator: getValidator().validate(form)
        alt バリデーションエラーあり
            Validator-->>Interceptor: violations
            Note over Interceptor: WARN ログ (行番号付き)<br/>本体は呼ばず null を返す
            Interceptor-->>Batch: null
        else エラーなし
            Validator-->>Interceptor: 空集合
            Interceptor->>Action: handle(form, ctx)
            Action->>BeanUtil: createAndCopy(ZipCodeData.class, form)
            BeanUtil-->>Action: ZipCodeData
            Action->>Dao: insert(data)
            Dao->>DB: INSERT
            DB-->>Dao: ok
            Action-->>Interceptor: Result.Success
            Interceptor-->>Batch: Result.Success
        end
    end

    Batch->>Reader: close(ctx)
    Reader->>Mapper: close()
```

---

## Components

### ImportZipCodeFileAction

**File**: [ImportZipCodeFileAction.java](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/action/ImportZipCodeFileAction.java)

- **Role**: `BatchAction<ZipCodeForm>` を継承し、住所CSVの1レコードを DB へ登録する業務ハンドラ。
- **Key methods**:
  - `handle(ZipCodeForm inputData, ExecutionContext ctx)` (:34-41) — `@ValidateData` により Bean Validation 済みデータを受け取り、`BeanUtil.createAndCopy` で `ZipCodeData` に変換後 `UniversalDao.insert` を実行、`Result.Success` を返却。
  - `createReader(ExecutionContext ctx)` (:48-51) — `new ZipCodeFileReader()` を返し、入力ソースとして登録する。
- **Dependencies**: `ZipCodeForm`, `ZipCodeData`, `ZipCodeFileReader`, `@ValidateData`, `BeanUtil`, `UniversalDao`, `BatchAction`, `DataReader`, `ExecutionContext`, `Result`。

### ZipCodeForm

**File**: [ZipCodeForm.java](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/form/ZipCodeForm.java)

- **Role**: CSV レコードをバインドしバリデーションするフォーム。クラスに `@Csv` / `@CsvFormat`、各プロパティに `@Required` / `@Domain("...")` を付与。`lineNumber` プロパティのゲッタに `@LineNumber` を付け、エラー行番号を自動設定する。
- **Key methods**:
  - `getLineNumber()` — `@LineNumber` を付与し Nablarch データバインドが現在行を設定する。
  - 各プロパティのゲッタ/セッタ — databind と BeanUtil から呼ばれる。
- **Dependencies**: `nablarch.common.databind.csv.@Csv`, `@CsvFormat`, `@LineNumber`, `nablarch.core.validation.ee.@Required`, `@Domain`。

### ZipCodeFileReader

**File**: [ZipCodeFileReader.java](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader/ZipCodeFileReader.java)

- **Role**: `DataReader<ZipCodeForm>` の実装。`ObjectMapperIterator` で CSV ストリームをラップし、1行ずつ `ZipCodeForm` を返す。
- **Key methods**:
  - `read(ExecutionContext)` — 初回に `initialize()` を呼び、`iterator.next()` で次の `ZipCodeForm` を返す。
  - `hasNext(ExecutionContext)` — `iterator.hasNext()` を返す。`false` で読込終了。
  - `close(ExecutionContext)` — `iterator.close()` でストリーム解放。
  - `initialize()` — `FilePathSetting.getInstance().getFileWithoutCreate("csv-input","importZipCode")` でファイル解決し、`ObjectMapperFactory.create(ZipCodeForm.class, FileInputStream)` で `ObjectMapper` を生成、`ObjectMapperIterator` でラップ。`FileNotFoundException` は `IllegalStateException` にラップして送出。
- **Dependencies**: `ObjectMapperFactory`, `ObjectMapperIterator`, `FilePathSetting`, `DataReader`, `ExecutionContext`, `ZipCodeForm`。

### ValidateData (インターセプタ)

**File**: [ValidateData.java](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/interceptor/ValidateData.java)

- **Role**: メソッドに付与されたデータレコードを Bean Validation する共通インターセプタアノテーション。`handle` メソッドをインターセプトし、エラーは WARN ログ出力のみで本体を実行しない。
- **Key methods**:
  - `ValidateDataImpl#handle(Object data, ExecutionContext context)` — `ValidatorUtil.getValidator().validate(data)` を実行。違反が空なら `getOriginalHandler().handle(data, context)` を呼び、違反があれば `BeanUtil.getProperty(data,"lineNumber")` で行番号を取得して `MessageUtil.createMessage(WARN, "invalid_data_record", propertyPath, message, lineNumber)` をロガーに出力し `null` を返す。
- **Dependencies**: `nablarch.fw.Interceptor`, `ValidatorUtil`, `BeanUtil`, `MessageUtil`, `Logger`。

---

## Nablarch Framework Usage

### BatchAction

**Class**: `nablarch.fw.action.BatchAction<TData>`

**Description**: Nablarch バッチの業務ハンドラ基底クラス。`createReader` で入力ソースを、`handle` でレコード毎の処理を実装する。

**Usage**:
```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {
    @Override @ValidateData
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) { ... }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader();
    }
}
```

**Important points**:
- ✅ **`handle` と `createReader` の実装**: `handle` に1レコード分の業務処理、`createReader` で使用するデータリーダを返す。
- 💡 **共通処理はインターセプタ化**: バッチ毎に差のない Bean Validation は `@ValidateData` のようなインターセプタで共通化する（本 Example の実装指針）。
- 🎯 **入力ソースは DataReader**: DB / CSV / 固定長など任意の入力は `DataReader` 実装で差し替える。

**Usage in this code**:
- `ImportZipCodeFileAction` (Line 20-52) で `BatchAction<ZipCodeForm>` を継承。
- `handle` (:34-41) に DB 登録、`createReader` (:48-51) で `ZipCodeFileReader` 生成。

**Details**: [Nablarch バッチ getting-started](../../.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md)

### UniversalDao

**Class**: `nablarch.common.dao.UniversalDao`

**Description**: Jakarta Persistence アノテーションを Entity に付けるだけで、SQL を書かずに登録/更新/削除/主キー検索などの単純 CRUD を実行できる DAO。

**Usage**:
```java
ZipCodeData data = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
UniversalDao.insert(data);
```

**Important points**:
- ✅ **Entity に Jakarta Persistence アノテーション**: `@Entity`, `@Id`, `@Table` などが Entity 側に必須。
- ⚠️ **スキーマ切替との併用不可**: JDBCラッパーの「SQL中スキーマ置換」機能はこの CRUD では使えない。環境毎切替が必要なら JDBCラッパーを使う。
- 💡 **SQL 不要**: JPA アノテーションから実行時に CRUD 文を組み立てるため、定型 INSERT/UPDATE/DELETE のコードを書かなくてよい。

**Usage in this code**:
- `ImportZipCodeFileAction#handle` (Line 40) で `UniversalDao.insert(data)` により `ZipCodeData` Entity を登録。

**Details**: [ユニバーサルDAO](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md)

### BeanUtil

**Class**: `nablarch.core.beans.BeanUtil`

**Description**: Bean 間のプロパティコピーやプロパティ取得などのユーティリティ。同名プロパティを自動マッピングする。

**Usage**:
```java
ZipCodeData data = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
Long lineNumber = (Long) BeanUtil.getProperty(data, "lineNumber");
```

**Important points**:
- ✅ **Form → Entity の詰め替えに使う**: バッチでは `ZipCodeForm` → `ZipCodeData` のように同名プロパティをまとめてコピー。
- 💡 **プロパティ取得も簡潔**: `BeanUtil.getProperty(bean, "name")` で動的にプロパティ値を取得でき、共通インターセプタから行番号等を取り出すのに便利。
- ⚠️ **`BeansException`**: プロパティが存在しない場合は例外。ValidateData では try/catch で無視している。

**Usage in this code**:
- `ImportZipCodeFileAction#handle` (Line 39) — `createAndCopy` で `ZipCodeData` を生成。
- `ValidateData.ValidateDataImpl#handle` — `BeanUtil.getProperty(data, "lineNumber")` で行番号取得。

**Details**: [BeanUtil](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md)

### Data Bind (`@Csv` / `@CsvFormat` / `@LineNumber` / ObjectMapper)

**Class**: `nablarch.common.databind.csv.*`, `nablarch.common.databind.ObjectMapperFactory`, `nablarch.common.databind.LineNumber`

**Description**: CSV / 固定長 / TSV などのレコードを Java Beans にマッピングするデータバインド機能。`ObjectMapperFactory.create(BeanClass, stream)` で `ObjectMapper` を得て `read()` / `write()` する。

**Usage**:
```java
@Csv(properties = {...}, type = CsvType.CUSTOM)
@CsvFormat(charset = "UTF-8", fieldSeparator = ',', lineSeparator = "\r\n",
           quote = '"', requiredHeader = false, emptyToNull = true)
public class ZipCodeForm {
    @LineNumber
    public Long getLineNumber() { return lineNumber; }
}

ObjectMapper<ZipCodeForm> mapper =
    ObjectMapperFactory.create(ZipCodeForm.class, new FileInputStream(file));
```

**Important points**:
- ✅ **`@Csv` と `@CsvFormat` をフォームに付与**: プロパティ順序・区切り文字・文字コード・ヘッダ有無を宣言する。
- 💡 **`@LineNumber` で行番号を自動設定**: エラーログに行番号を出したいときは `Long` プロパティのゲッタに付与。
- ⚠️ **`ObjectMapper` は close する**: リソース解放必須。本例では `ObjectMapperIterator#close` 経由で閉じている。

**Usage in this code**:
- `ZipCodeForm` に `@Csv`, `@CsvFormat`, `@LineNumber` を付与（行番号は `getLineNumber()`）。
- `ZipCodeFileReader#initialize()` で `ObjectMapperFactory.create(ZipCodeForm.class, FileInputStream)` を生成、`ObjectMapperIterator` でラップ。

**Details**: [データバインド](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md)

### Bean Validation (`@Required` / `@Domain` / ValidatorUtil)

**Class**: `nablarch.core.validation.ee.*`, `nablarch.core.validation.ee.ValidatorUtil`

**Description**: Jakarta Bean Validation を Nablarch 拡張付きで実行する仕組み。`@Required` や `@Domain` で宣言し、`ValidatorUtil.getValidator().validate(bean)` で実行する。

**Usage**:
```java
@Domain("zipCode") @Required private String zipCode7digit;

Validator validator = ValidatorUtil.getValidator();
Set<ConstraintViolation<Object>> violations = validator.validate(data);
```

**Important points**:
- ✅ **`@Domain` でドメイン型制約を宣言**: `DomainManager` に登録されたドメイン別の制約（桁数・文字種など）を付与。
- ⚠️ **違反時の扱いを決める**: バッチでは本例のように「該当行のみスキップして警告ログ」にする設計が一般的。
- 💡 **インターセプタで共通化**: `@ValidateData` のようにインターセプタ化すると全バッチで一貫したバリデーション挙動になる。

**Usage in this code**:
- `ZipCodeForm` の各プロパティに `@Required` / `@Domain("...")`。
- `ValidateData.ValidateDataImpl#handle` で `ValidatorUtil.getValidator().validate(data)` を実行し、違反時は WARN ログ出力のみで本体を呼ばない。

**Details**: [Bean Validation](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md)

### FilePathSetting

**Class**: `nablarch.core.util.FilePathSetting`

**Description**: 論理ベースパス（例: `csv-input`）と論理ファイル名から物理ファイルを解決するユーティリティ。環境依存のパスを設定ファイル側に寄せられる。

**Usage**:
```java
File file = FilePathSetting.getInstance()
                           .getFileWithoutCreate("csv-input", "importZipCode");
```

**Important points**:
- ✅ **論理名でファイル指定**: コード中に物理パスを書かず、設定で差し替え可能にする。
- 🎯 **入出力ファイル管理**: バッチ入力 CSV・フォーマット定義ファイル・出力ファイルなどの場所を一元管理する用途。

**Usage in this code**:
- `ZipCodeFileReader#initialize()` で `FilePathSetting.getInstance().getFileWithoutCreate("csv-input", "importZipCode")` により入力 CSV を解決。

**Details**: [ファイルパス管理](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-file-path-management.md)

### Interceptor

**Class**: `nablarch.fw.Interceptor`, `nablarch.fw.Interceptor.Impl`

**Description**: ハンドラ実行前後に処理を挟み込む仕組み。`@Interceptor(Impl.class)` を付けたアノテーションを任意の `handle` メソッドに適用すると、`Interceptor.Impl#handle` がラップして呼ばれる。

**Usage**:
```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Interceptor(ValidateData.ValidateDataImpl.class)
public @interface ValidateData {
    class ValidateDataImpl extends Interceptor.Impl<Object, Result, ValidateData> {
        @Override public Result handle(Object data, ExecutionContext ctx) {
            // バリデーション
            return getOriginalHandler().handle(data, ctx);
        }
    }
}
```

**Important points**:
- ✅ **`getOriginalHandler().handle(...)` で本体委譲**: 条件を満たすときのみ本体を呼ぶ／呼ばないを制御可能。
- 💡 **アノテーション駆動でクロスカッティング関心事を分離**: バリデーション・ロギングなどを一箇所に集約できる。

**Usage in this code**:
- `@ValidateData` が `ImportZipCodeFileAction#handle` に付与されており、実体 `ValidateDataImpl` が Bean Validation を実行してから本体 `handle` を呼び出す。

**Details**: [Nablarch バッチ getting-started](../../.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md)

---

## References

### Source Files

- [ImportZipCodeFileAction.java (.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/action)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/action/ImportZipCodeFileAction.java) - ImportZipCodeFileAction
- [ImportZipCodeFileAction.java (.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/action)](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/action/ImportZipCodeFileAction.java) - ImportZipCodeFileAction
- [ZipCodeForm.java (.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/form)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/form/ZipCodeForm.java) - ZipCodeForm
- [ZipCodeForm.java (.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/form)](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/form/ZipCodeForm.java) - ZipCodeForm
- [ZipCodeFileReader.java (.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader/ZipCodeFileReader.java) - ZipCodeFileReader
- [ZipCodeFileReader.java (.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader)](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/reader/ZipCodeFileReader.java) - ZipCodeFileReader
- [ValidateData.java (.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/interceptor)](../../.lw/nab-official/v5/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/interceptor/ValidateData.java) - ValidateData
- [ValidateData.java (.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/interceptor)](../../.lw/nab-official/v6/nablarch-example-batch/src/main/java/com/nablarch/example/app/batch/interceptor/ValidateData.java) - ValidateData

### Knowledge Base (Nabledge-6)

- [Nablarch Batch Getting Started Nablarch Batch](../../.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md)
- [Libraries Universal Dao](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md)
- [Libraries Data Bind](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-data-bind.md)
- [Libraries Bean Validation](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-validation.md)
- [Libraries Bean Util](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-bean-util.md)
- [Libraries File Path Management](../../.claude/skills/nabledge-6/docs/component/libraries/libraries-file-path-management.md)

### Official Documentation

(No official documentation links available)

---

**Output**: `.nabledge/20260424/code-analysis-ImportZipCodeFileAction.md`

**Note**: This documentation was generated by the code-analysis workflow of the nabledge-6 skill.
