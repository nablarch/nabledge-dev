# 汎用データフォーマット

## 機能概要

標準でサポートするフォーマット: 固定長、可変長（CSV/TSVなど）、JSON、XML。固定長と可変長はマルチレイアウトデータ（レコードごとに異なるレイアウト）にも対応。

> **重要**: 本機能には以下のデメリットがあるため、原則**非推奨**（やむを得ない場合を除く）。:ref:`messaging` は内部で本機能を使用しているため代替機能使用不可。
> - 複雑な :ref:`data_format-format_definition_file` の作成が必要
> - 入出力が `Map` に限定。フィールド名を文字列指定のためIDEの補完不可・ダウンキャストが必要（誤ると実行時例外）
> - `BeanUtil` を不使用のため他機能とマッピング方法が異なる
> - フォーマットによってMapの扱いが異なる（例：必須項目にnullを指定した場合、XMLは空文字出力、JSONは必須例外送出）
> - 出力データによってはJSONの仕様を満たせない（例：`数値型` に「data」などの文字列を渡すと `{"number":data}` のような不正なJSONが出力される）
> - `DataType` の実装クラスがフォーマットごとに異なり拡張しにくく、設定誤りは実行時まで検知不可

**代替機能**:

| フォーマット | 代替機能 |
|---|---|
| 固定長 | :ref:`data_bind` |
| 可変長 | :ref:`data_bind` |
| XML | [Jakarta XML Binding](https://jakarta.ee/specifications/xml-binding/) |
| JSON | OSSを推奨（例: [Jackson(外部サイト、英語)](https://github.com/FasterXML/jackson)） |

文字列・10進数数値に加え、パック数値・ゾーン10進数形式に対応。UTF-8、Shift_JIS、EBCDICなどに対応（JVMがサポートする文字セットが使用可能）。

固定長ファイルのスペース・ゼロ(0)パディングおよびトリミングに対応。アプリケーション側での処理不要。詳細は :ref:`data_format-field_convertor_list` 参照。

## モジュール一覧

**モジュール**:

```xml
<!-- 汎用データフォーマット -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core-dataformat</artifactId>
</dependency>

<!-- アップロードヘルパーまたはファイルダウンロードを使用する場合 -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web-extension</artifactId>
</dependency>
```

## 入出力データのフォーマットを定義する

フォーマット定義ファイルはテキストファイル形式で作成する。詳細仕様は [data_format/format_definition](libraries-format_definition.md) 参照。

```bash
file-type:        "Variable" # 可変長
text-encoding:    "MS932"    # 文字列型フィールドの文字エンコーディング
record-separator: "\r\n"     # 改行コード(crlf)
field-separator:  ","        # csv

# レコード識別フィールドの定義
[Classifier]
1 dataKbn X     # 1つめのフィールド
3 type    X     # 3つめのフィールド

[parentData]
dataKbn = "1"
type    = "01"
1 dataKbn X
2 ?filler X
3 type    X
4 data    X

[childData]
dataKbn = "1"
type    = "02"
1 dataKbn X
2 ?filler X
3 type    X
4 data    X
```

## ファイルにデータを出力する

**クラス**: `nablarch.common.io.FileRecordWriterHolder`

- 書き込むデータは `Map` として準備
- Mapのキー値は :ref:`data_format-format_definition_file` で定義したフィールド名（大文字・小文字区別なし）
- `open` メソッドでファイルリソースを書き込み可能状態にする
- `write` メソッドでデータをファイルに書き込む

```java
Map<String, Object> user = new HashMap<>();
user.put("name", "名前");
user.put("age", 20);

FileRecordWriterHolder.open("users.csv", "user_csv_format");
FileRecordWriterHolder.write(user, "user.csv");
```

> **補足**: `FileRecordWriterHolder` を使用するには、フォーマット定義ファイルの配置ディレクトリや出力先ディレクトリを :ref:`file_path_management` に設定すること。

> **重要**: `FileRecordWriterHolder` で開いたファイルリソースは :ref:`file_record_writer_dispose_handler` で自動開放される。:ref:`file_record_writer_dispose_handler` を必ずハンドラキュー上に設定すること。

> **重要**: 出力データに不正な値が設定されている場合に正しく処理できない可能性があるため、事前にアプリケーション側でバリデーションを行うこと。

> **重要**: デフォルトは1レコードごとにファイルへ書き込む。大量データ出力時に性能要件を満たせない場合は、`DataFormatConfig` の `flushEachRecordInWriting` を `false` に設定してバッファサイズ単位で書き込むよう変更すること。バッファサイズは `FileRecordWriterHolder` の `open` メソッドで指定可能。

```xml
<component name="dataFormatConfig" class="nablarch.core.dataformat.DataFormatConfig">
  <property name="flushEachRecordInWriting" value="false" />
</component>
```

## ファイルダウンロードで使用する

**クラス**: `nablarch.common.web.download.DataRecordResponse`

- `DataRecordResponse` 生成時にフォーマット定義ファイルの論理パス名とファイル名を指定
- `DataRecordResponse#write` でデータ出力（複数レコードは繰り返し呼び出し）
- `Content-Type` および `Content-Disposition` を設定
- 業務アクションから `DataRecordResponse` を返却

```java
public HttpResponse download(HttpRequest request, ExecutionContext context) {
    Map<String, Object> user = new hashMap<>();
    user.put("name", "なまえ");
    user.put("age", 30);

    DataRecordResponse response = new DataRecordResponse("format", "users_csv");
    response.write(user);
    response.setContentType("text/csv; charset=Shift_JIS");
    response.setContentDisposition("メッセージ一覧.csv");

    return response;
}
```

> **補足**: フォーマット定義ファイルの格納パスは :ref:`file_path_management` に設定すること。

## アップロードしたファイルを読み込む

アップロードファイルの読み込み方法は2種類。**汎用データフォーマットのみを使った読み込み（推奨）**を使用すること。

### 汎用データフォーマットのみを使った読み込み（推奨）

- `HttpRequest#getPart` でアップロードファイルを取得（引数はパラメータ名）
- `FilePathSetting` からフォーマット定義ファイルの `File` オブジェクトを取得
- `FormatterFactory` から `DataRecordFormatter` を生成
- `DataRecordFormatter` に `InputStream` を設定（`mark`/`reset` サポートが必要なため `BufferedInputStream` でラップ）
- `hasNext()` でループし `readRecord()` でレコード読み込み（戻り値は `DataRecord`）
- `BeanUtil` で `DataRecord` からJava Beansへマッピング可能（例: `BeanUtil.createAndCopy(Users.class, record)`）

```java
public HttpResponse upload(HttpRequest req, ExecutionContext ctx) {
    final List<PartInfo> partInfoList = request.getPart("users");
    final File format = FilePathSetting.getInstance()
                                       .getFile("format", "users-layout");
    try (final DataRecordFormatter formatter = FormatterFactory.getInstance()
                                                               .createFormatter(format)) {
        formatter.setInputStream(new BufferedInputStream(partInfoList.get(0).getInputStream()))
                 .initialize();
        while (formatter.hasNext()) {
            final DataRecord record = formatter.readRecord();
            final Users users = BeanUtil.createAndCopy(Users.class, record);
        }
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}
```

### アップロードヘルパーを使った読み込み（非推奨）

`UploadHelper` を使用すると読み込み・バリデーション・DB保存を簡易実行できるが、以下の制限があるため**非推奨**:
- 入力値チェックは :ref:`nablarch_validation` のみ（推奨される :ref:`bean_validation` が使用不可）
- 拡張難易度が高い

```java
PartInfo partInfo = req.getPart("fileToSave").get(0);
UploadHelper helper = new UploadHelper(partInfo);
int cnt = helper
    .applyFormat("N11AC002")
    .setUpMessageIdOnError("format.error", "validation.error", "file.empty.error")
    .validateWith(UserInfoTempEntity.class, "validateRegister")  // BulkValidator
    .importWith(this, "INSERT_SQL");                              // BulkValidationResult
```

## JSONやXMLの階層構造のデータを読み書きする

JSONやXMLの階層構造データをMapで読み書きする際、各階層の要素名をドット(`.`)で連結したキー値を使用する。

**Mapのキー規則**:
- 階層構造: `親要素名.子要素名` 形式
- 深い階層: さらに`.`で連結
- 最上位要素名はキーに含めない
- 配列要素: 添字(0始まり)を付加 (例: `user[0].name`)

> **重要**: 親要素が任意で、親要素が存在する場合のみ子要素を必須とする設定には対応していない。階層構造のデータは全て任意項目として定義することを推奨する。

**フォーマット定義ファイル例** (JSONの場合は`file-type`を`JSON`に変更、定義方法は :ref:`data_format-nest_object` 参照):
```bash
file-type:        "XML"
text-encoding:    "UTF-8"

[users]              # ルート要素
1 user    [0..*] OB

[user]               # ネストした要素
1 name    [0..1] N
2 age     [0..1] X9
3 address [0..1] N
```

**Java (Map設定例)**:
```java
Map<String, Object> data = new HashMap<String, Object>();
data.put("user[0].name", "なまえ1");
data.put("user[0].address", "住所1");
data.put("user[0].age", 30);
data.put("user[1].name", "なまえ2");
data.put("user[1].address", "住所2");
data.put("user[1].age", 31);
```

**XML出力例**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<users>
  <user>
    <name>なまえ1</name>
    <address>住所1</address>
    <age>30</age>
  </user>
  <user>
    <name>なまえ2</name>
    <address>住所2</address>
    <age>31</age>
  </user>
</users>
```

**JSON出力例**:
```json
{
  "user": [
    {"name": "なまえ1", "address": "住所1", "age": 30},
    {"name": "ななえ2", "address": "住所2", "age": 31}
  ]
}
```

## XMLでDTDを使う

> **重要**: XMLを入力する場合、DTDはデフォルトで使用不可。DTDを使用したXMLを読み込もうとすると例外が発生する。これは[XML外部実体参照(XXE)](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)を防止するための措置。

読み込み対象XMLが信頼できる場合のみ、`XmlDataParser` の `allowDTD` プロパティを`true`に設定してDTDの使用を許可できる。コンポーネント名は`XmlDataParser`で明示的に設定する。

```xml
<component name="XmlDataParser" class="nablarch.core.dataformat.XmlDataParser">
  <!-- DTDの使用を許可する。XXE攻撃の危険性があるため、信頼できるXML以外には使用してはならない。 -->
  <property name="allowDTD" value="true" />
</component>
```

## XMLで名前空間を使う

接続先システムとの要件で名前空間が必要な場合、フォーマット定義ファイルで名前空間を定義する。

**ポイント**:
- 名前空間は `?@xmlns:名前空間` としてタイプ`X`、フィールドコンバータにURIを指定
- 要素名は `名前空間:要素名` 形式で表す
- MapのキーはキャメルケースHandに変換: `名前空間+要素名(先頭大文字)` 形式 (例: `testnsKey1`)

**フォーマット定義ファイル例**:
```bash
file-type:        "XML"
text-encoding:    "UTF-8"

[testns:data]
1 ?@xmlns:testns X "http://testns.hoge.jp/apply"
2 testns:key1 X
```

**XMLデータ例**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testns:data xmlns:testns="http://testns.hoge.jp/apply">
  <testns:key1>value1</testns:key1>
</testns:data>
```

**Mapデータ例**:
```java
Map<String, Object> data = new HashMap<String, Object>();
data.put("testnsKey1", "value1");
```

## XMLで属性を持つ要素にコンテンツを定義する

XMLで属性を持つ要素にコンテンツを定義するには、フォーマット定義ファイルにコンテンツを表すフィールド名 `body` を使用する。デフォルトのフィールド名を変更する場合は :ref:`data_format-xml_content_name_change` を参照。

**フォーマット定義ファイル例**:
```bash
file-type:        "XML"
text-encoding:    "UTF-8"

[parent]
1 child   OB

[child]
1 @attr   X
2 body    X
```

**XMLデータ例**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<parent>
  <child attr="value1">value2</child>
</parent>
```

**Mapデータ例**:
```java
Map<String, Object> data = new HashMap<String, Object>();
data.put("child.attr", "value1");
data.put("child.body", "value2");
```

## 文字の置き換え（寄せ字）を行う

寄せ字機能により、外部データ読み込み時にシステムで使用可能な文字に置き換えられる。

**置き換えルール (propertiesファイル)**:
- `置き換え前の文字=置き換え後の文字` 形式
- 置き換え前・後はともに1文字のみ (サロゲートペア非対応)
- 記述ルール: `Properties` 参照

```properties
髙=高
﨑=崎
唖=■
```

> **補足**: 接続先ごとに置き換えルールを定義する場合は、複数のpropertiesファイルを作成する。

**コンポーネント設定**: `CharacterReplacementManager` をコンポーネント名 `characterReplacementManager` で設定。`configList` プロパティに `CharacterReplacementConfig` のリストを設定。複数のpropertiesファイルを定義する場合は `typeName` プロパティに異なる名前を設定。

```xml
<component name="characterReplacementManager"
    class="nablarch.core.dataformat.CharacterReplacementManager">
  <property name="configList">
    <list>
      <component class="nablarch.core.dataformat.CharacterReplacementConfig">
        <property name="typeName" value="a_system"/>
        <property name="filePath" value="classpath:a-system.properties"/>
        <property name="encoding" value="UTF-8"/>
      </component>
      <component class="nablarch.core.dataformat.CharacterReplacementConfig">
        <property name="typeName" value="b_system"/>
        <property name="filePath" value="classpath:b-system.properties"/>
        <property name="encoding" value="UTF-8"/>
      </component>
    </list>
  </property>
</component>
```

**初期化コンポーネント設定**:
```xml
<component name="initializer"
    class="nablarch.core.repository.initialization.BasicApplicationInitializer">
  <property name="initializeList">
    <list>
      <component-ref name="characterReplacementManager" />
    </list>
  </property>
</component>
```

**フォーマット定義での使用**: :ref:`replacement <data_format-replacement_convertor>` を使用し、引数に `typeName` を指定する。

```bash
# Aシステムとの置き換えルールを適用
1 name N(100) replacement("a_system")

# Bシステムとの置き換えルールを適用
1 name N(100) replacement("b_system")
```

## 出力するデータの表示形式をフォーマットする

データ出力時に日付・数値などの表示形式をフォーマットするには :ref:`format` を使用する。詳細は :ref:`format` を参照。

## 拡張例

## フィールドタイプを追加する

:ref:`data_format-field_type_list` で要件を満たせない場合（例: 文字列タイプのパディング文字がバイナリの場合）、プロジェクト固有のフィールドタイプを定義して対応する。

**手順:**
1. `DataType` を実装したクラスを作成する
2. フォーマットに応じたファクトリの継承クラスを作成する
3. 作成したファクトリクラスを設定クラスのプロパティに設定する

> **補足**: 標準のフィールドタイプ実装は `nablarch.core.dataformat.convertor.datatype` パッケージ配下に配置されている。

**フォーマット毎のファクトリクラス:**

| フォーマット | ファクトリクラス |
|---|---|
| Fixed(固定長) | `FixedLengthConvertorFactory` |
| Variable(可変長) | `VariableLengthConvertorFactory` |
| JSON | `JsonDataConvertorFactory` |
| XML | `XmlDataConvertorFactory` |

Fixed(固定長)の実装例:

```java
public class CustomFixedLengthConvertorFactory extends FixedLengthConvertorFactory {
    @Override
    protected Map<String, Class<?>> getDefaultConvertorTable() {
        final Map<String, Class<?>> defaultConvertorTable = new CaseInsensitiveMap<Class<?>>(new ConcurrentHashMap<String, Class<?>>(super.getDefaultConvertorTable()));
        defaultConvertorTable.put("custom", CustomType.class);
        return Collections.unmodifiableMap(defaultConvertorTable);
    }
}
```

**フォーマット毎の設定クラスとプロパティ:**

| フォーマット | 設定クラス名(コンポーネント名) | プロパティ名 |
|---|---|---|
| Fixed(固定長) | `FixedLengthConvertorSetting` (fixedLengthConvertorSetting) | `fixedLengthConvertorFactory` |
| Variable(可変長) | `VariableLengthConvertorSetting` (variableLengthConvertorSetting) | `variableLengthConvertorFactory` |
| JSON | `JsonDataConvertorSetting` (jsonDataConvertorSetting) | `jsonDataConvertorFactory` |
| XML | `XmlDataConvertorSetting` (xmlDataConvertorSetting) | `xmlDataConvertorFactory` |

Fixed(固定長)の設定例:

```xml
<component name="fixedLengthConvertorSetting"
    class="nablarch.core.dataformat.convertor.FixedLengthConvertorSetting">
  <property name="fixedLengthConvertorFactory">
    <component class="com.sample.CustomFixedLengthConvertorFactory" />
  </property>
</component>
```

> **重要**: `convertorTable` プロパティでのフィールドタイプ追加は非推奨。理由: (1) 追加したいフィールドタイプだけでなく、デフォルトのフィールドタイプも全て設定が必要で、バージョンアップ時に自動適用されず手動修正が必要になる。(2) デフォルト定義はファクトリクラスに実装されており、設定ミスを起こしやすい。

## XMLで属性を持つ要素のコンテンツ名を変更する

属性を持つ要素のコンテンツ名を変更するには、以下のクラスの `contentName` プロパティに変更後のコンテンツ名を設定する。

- `XmlDataParser`
- `XmlDataBuilder`

**ポイント:**
- `XmlDataParser` のコンポーネント名は `XmlDataParser` とすること
- `XmlDataBuilder` のコンポーネント名は `XmlDataBuilder` とすること

```xml
<component name="XmlDataParser" class="nablarch.core.dataformat.XmlDataParser">
  <property name="contentName" value="change" />
</component>

<component name="XmlDataBuilder" class="nablarch.core.dataformat.XmlDataBuilder">
  <property name="contentName" value="change" />
</component>
```
