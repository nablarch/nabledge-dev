# 汎用データフォーマット

## 機能概要

汎用データフォーマットは固定長、可変長（CSV/TSVなど）、JSON、XMLの入出力に対応する。固定長・可変長ではレコード毎にレイアウトの異なるマルチレイアウトデータにも対応（XMLとJSONにはレコードという概念が存在しない）。

![汎用データフォーマット 構成図](../../knowledge/component/libraries/assets/libraries-data_format/structure.png)

> **重要**: 本機能には以下のデメリットがあるため、**やむを得ない場合を除き非推奨**。:ref:`messaging` は内部で本機能を使用しているため代替機能を使用できない。
>
> - 複雑な :ref:`フォーマット定義ファイル <data_format-format_definition_file>` の作成が必要
> - 入出力が `Map` に限定され、フィールド名を文字列で指定するためIDEの補完が使えず実装誤りを起こしやすい。Mapから取り出した値のダウンキャストが必要で誤ると実行時に例外が送出される
> - `BeanUtil` を使用しないため他機能とマッピング方法が異なる
> - フォーマットによってMapの扱いが異なるため、同一データを複数フォーマットに対応させると例外が発生する場合がある（例：必須項目にnullを指定した場合、XMLは空文字出力、JSONは例外送出）
> - `数値型` や `真偽値型` を使用し対応しないデータ型を出力すると不正なJSONが出力される（例：数値型で"data"を出力すると `{"number":data}` のような不正なJSON）
> - データ形式によって使用できる `データタイプ` の実装クラスが異なり拡張しづらく、設定誤りは実行時まで検知できない

**代替機能**:
- 固定長: :ref:`data_bind` を使用
- 可変長: :ref:`data_bind` を使用
- XML: [Jakarta XML Binding](https://jakarta.ee/specifications/xml-binding/) を推奨
- JSON: OSSを推奨（例: [Jackson(外部サイト、英語)](https://github.com/FasterXML/jackson)）

**文字セット・データ形式サポート**:
- 文字列・10進数に加え、パック数値・ゾーン10進数形式に対応
- UTF-8・Shift_JIS・EBCDICなどの文字セットに対応

> **補足**: 文字セットは実行環境のJVMでサポートされているものが使用できる。

- 固定長ファイルのスペース・ゼロパディング/トリミングに対応（アプリ側での処理不要）。詳細は :ref:`data_format-field_convertor_list` を参照

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

入出力データのフォーマット定義はフォーマット定義ファイル（テキストファイル）に記述する。詳細仕様は [data_format/format_definition](libraries-format_definition.md) を参照。

設定例（可変長CSV・マルチレイアウト）:
```bash
file-type:        "Variable" # 可変長
text-encoding:    "MS932"    # 文字列型フィールドの文字エンコーディング
record-separator: "\r\n"     # 改行コード(crlf)
field-separator:  ","        # csv

[Classifier]
1 dataKbn X
3 type    X

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

`FileRecordWriterHolder` を使用してファイルへデータを出力する。

- 書き込みデータは `Map` として準備し、キーはフォーマット定義ファイルで定義したフィールド名（大文字小文字区別なし）を指定
- `open` メソッドでファイルリソースを書き込み可能状態にしてから `write` メソッドで書き込む

```java
Map<String, Object> user = new HashMap<>();
user.put("name", "名前");
user.put("age", 20);
FileRecordWriterHolder.open("users.csv", "user_csv_format");
FileRecordWriterHolder.write(user, "user.csv");
```

> **重要**: `FileRecordWriterHolder` で開いたファイルリソースは :ref:`file_record_writer_dispose_handler` で自動開放される。必ず :ref:`file_record_writer_dispose_handler` をハンドラキュー上に設定すること。

> **重要**: 出力するデータに不正な値が設定されていた場合に正しく処理できない可能性があるため、事前にアプリケーション側で不正な値でないかをチェックすること。

> **重要**: デフォルトでは1レコード毎にファイルへ書き込む。大量データ出力時に性能要件を満たせない場合は、バッファサイズ単位での書き込みに変更すること。`DataFormatConfig` コンポーネントに `flushEachRecordInWriting=false` を設定し、バッファサイズは `open` メソッドで指定する。

```xml
<component name="dataFormatConfig" class="nablarch.core.dataformat.DataFormatConfig">
  <property name="flushEachRecordInWriting" value="false" />
</component>
```

> **補足**: `FileRecordWriterHolder` を使用するには、フォーマット定義ファイルの配置ディレクトリと出力先ディレクトリを :ref:`file_path_management` に設定すること。

## ファイルダウンロードで使用する

`DataRecordResponse` を使用してファイルダウンロード形式でクライアントに応答する。

- `DataRecordResponse` 生成時にフォーマット定義ファイルの論理パス名とファイル名を指定
- `DataRecordResponse#write` でデータ出力（複数レコードは繰り返し呼び出し）
- `Content-Type` と `Content-Disposition` を設定して `DataRecordResponse` を返却

```java
public HttpResponse download(HttpRequest request, ExecutionContext context) {
    Map<String, Object> user = new hashMap<>()
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

アップロードファイルの読み込み方法は2種類ある。アップロードヘルパーには制限があるため、**汎用データフォーマットのみを使った方法を推奨**する。

#### 汎用データフォーマットのみを使った読み込み（推奨）

- `HttpRequest#getPart` でアップロードファイルを取得（引数はパラメータ名）
- `FilePathSetting` からフォーマット定義ファイルの `File` オブジェクトを取得
- `FormatterFactory` から `DataRecordFormatter` を生成
- `DataRecordFormatter` に設定する `InputStream` は mark/reset がサポートされている必要があるため `BufferedInputStream` でラップすること

```java
public HttpResponse upload(HttpRequest req, ExecutionContext ctx) {
    final List<PartInfo> partInfoList = request.getPart("users");
    final File format = FilePathSetting.getInstance().getFile("format", "users-layout");

    try (final DataRecordFormatter formatter = FormatterFactory.getInstance().createFormatter(format)) {
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

#### アップロードヘルパーを使った読み込み（非推奨）

> **重要**: 以下の制限があるため非推奨。汎用データフォーマットのみを使った方法を使用すること。
> - 入力値チェックが :ref:`nablarch_validation` に限定され、推奨される :ref:`bean_validation` が使用不可
> - 拡張が難しく、要件を満たす実装が容易でない

`UploadHelper` でファイル読み込み・バリデーション・DB保存を簡易実行できる。

- `UploadHelper#applyFormat` でフォーマット定義ファイルを設定
- `setUpMessageIdOnError` でバリデーションエラー用メッセージIDを設定
- `validateWith` でバリデーションを実行するBeanクラスとメソッドを設定
- `importWith` でDB登録

```java
public HttpResponse upload(HttpRequest req, ExecutionContext ctx) {
    PartInfo partInfo = req.getPart("fileToSave").get(0);

    UploadHelper helper = new UploadHelper(partInfo);
    int cnt = helper
        .applyFormat("N11AC002")
        .setUpMessageIdOnError("format.error", "validation.error", "file.empty.error")
        .validateWith(UserInfoTempEntity.class, "validateRegister")
        .importWith(this, "INSERT_SQL");
}
```

## フィールドタイプを追加する

## フィールドタイプを追加する

:ref:`data_format-field_type_list` の標準データタイプで要件を満たせない場合（例：文字列タイプのパディング文字がバイナリ）は、プロジェクト固有のフィールドタイプを定義する。

手順:
1. `DataType` 実装クラスを作成する
2. フォーマットに応じたファクトリの継承クラスを作成する
3. 作成したファクトリクラスをフォーマットに応じた設定クラスのプロパティに設定する

> **補足**: 標準のフィールドタイプ実装は `nablarch.core.dataformat.convertor.datatype` パッケージ配下に配置されている。実装追加の際は参考にすること。

フォーマット別ファクトリクラス:

| フォーマット | ファクトリクラス |
|---|---|
| Fixed(固定長) | `FixedLengthConvertorFactory` |
| Variable(可変長) | `VariableLengthConvertorFactory` |
| JSON | `JsonDataConvertorFactory` |
| XML | `XmlDataConvertorFactory` |

Fixed(固定長)の継承クラス実装例:

```java
public class CustomFixedLengthConvertorFactory extends FixedLengthConvertorFactory {
    @Override
    protected Map<String, Class<?>> getDefaultConvertorTable() {
        final Map<String, Class<?>> defaultConvertorTable = new CaseInsensitiveMap<Class<?>>(
                new ConcurrentHashMap<String, Class<?>>(super.getDefaultConvertorTable()));
        defaultConvertorTable.put("custom", CustomType.class);
        return Collections.unmodifiableMap(defaultConvertorTable);
    }
}
```

フォーマット別設定クラスとプロパティ:

| フォーマット | 設定クラス(コンポーネント名) | プロパティ名 |
|---|---|---|
| Fixed(固定長) | `FixedLengthConvertorSetting` (fixedLengthConvertorSetting) | fixedLengthConvertorFactory |
| Variable(可変長) | `VariableLengthConvertorSetting` (variableLengthConvertorSetting) | variableLengthConvertorFactory |
| JSON | `JsonDataConvertorSetting` (jsonDataConvertorSetting) | jsonDataConvertorFactory |
| XML | `XmlDataConvertorSetting` (xmlDataConvertorSetting) | xmlDataConvertorFactory |

Fixed(固定長)の設定例:

```xml
<component name="fixedLengthConvertorSetting"
    class="nablarch.core.dataformat.convertor.FixedLengthConvertorSetting">
  <property name="fixedLengthConvertorFactory">
    <component class="com.sample.CustomFixedLengthConvertorFactory" />
  </property>
</component>
```

> **重要**: 設定クラスの `convertorTable` プロパティによるフィールドタイプ追加は推奨しない。理由: (1) 追加したいタイプだけでなくデフォルトタイプも全て設定し直す必要があり、バージョンアップ時にデフォルトが変更されても自動適用されず手動修正が必要になる。(2) デフォルト定義はファクトリクラスに実装されており、ソースコードを参照しながらコンポーネント設定ファイルに追加するため設定ミスを起こしやすい。

## XMLで属性を持つ要素のコンテンツ名を変更する

## XMLで属性を持つ要素のコンテンツ名を変更する

属性を持つ要素のコンテンツ名を変更するには、以下のクラスをコンポーネント設定ファイルに設定し `contentName` プロパティに変更後のコンテンツ名を設定する。

- `XmlDataParser`（コンポーネント名: `XmlDataParser`）
- `XmlDataBuilder`（コンポーネント名: `XmlDataBuilder`）

```xml
<component name="XmlDataParser" class="nablarch.core.dataformat.XmlDataParser">
  <property name="contentName" value="change" />
</component>

<component name="XmlDataBuilder" class="nablarch.core.dataformat.XmlDataBuilder">
  <property name="contentName" value="change" />
</component>
```

## JSONやXMLの階層構造のデータを読み書きする

JSONやXMLの階層構造データを読み込んだ場合、Mapのキー値は各階層の要素名をドット(`.`)で連結した値になる。

ポイント:
- 「親要素名.子要素名」形式でMapに値を設定
- 階層が深い場合はさらに`.`で連結
- 最上位の要素名はキーに含めない
- 配列要素の場合は添字(0始まり)を設定: `user[0].name`

> **重要**: 親要素が任意であり、親要素が存在する場合のみ子要素を必須、といった設定には対応していない。階層構造のデータをフォーマット定義ファイルに定義する際は、全て任意項目として定義することを推奨する。

フォーマット定義ファイル（JSONの場合は`file-type`を`JSON`に変更。階層構造の定義方法は:ref:`data_format-nest_object`参照）:

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

Mapの設定例:

```java
Map<String, Object> data = new HashMap<String, Object>();
data.put("user[0].name", "なまえ1");
data.put("user[0].address", "住所1");
data.put("user[0].age", 30);
data.put("user[1].name", "なまえ2");
data.put("user[1].address", "住所2");
data.put("user[1].age", 31);
```

出力XML:

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

出力JSON:

```json
{
  "user": [
    {"name": "なまえ1", "address": "住所1", "age": 30},
    {"name": "ななえ2", "address": "住所2", "age": 31}
  ]
}
```

## XMLでDTDを使う

> **重要**: XMLを入力する場合、DTDはデフォルトで使用不可。DTDを含むXMLを読み込もうとすると例外が発生する。これは[XML外部実体参照(XXE)](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)を防止するための措置。

信頼できるXMLのみDTDを許可する場合は、`XmlDataParser`の`allowDTD`プロパティを`true`に設定する。コンポーネント名は`XmlDataParser`で明示的に定義すること。

```xml
<component name="XmlDataParser" class="nablarch.core.dataformat.XmlDataParser">
  <!--
      DTDの使用を許可する。
      XXE攻撃の危険性があるため、信頼できるXML以外には使用してはならない。
   -->
  <property name="allowDTD" value="true" />
</component>
```

## XMLで名前空間を使う

接続先システムとの要件で名前空間を使用する場合、フォーマット定義ファイルで名前空間を定義する。

ポイント:
- 名前空間は使用する要素に`?@xmlns:名前空間`として定義。タイプは`X`、フィールドコンバータ部にURIを指定
- 名前空間の表記: 「名前空間:要素名」形式
- MapのキーはJ「名前空間＋要素名（先頭大文字）」となる

フォーマット定義ファイル:

```bash
file-type:        "XML"
text-encoding:    "UTF-8"

[testns:data]
1 ?@xmlns:testns X "http://testns.hoge.jp/apply"
2 testns:key1 X
```

対応XMLデータ:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testns:data xmlns:testns="http://testns.hoge.jp/apply">
  <testns:key1>value1</testns:key1>
</testns:data>
```

Mapデータ（キーは「名前空間＋要素名先頭大文字」形式）:

```java
Map<String, Object> data = new HashMap<String, Object>();
data.put("testnsKey1", "value1");
```

## XMLで属性を持つ要素にコンテンツを定義する

XMLで属性を持つ要素にコンテンツを定義する場合、フォーマット定義ファイルにコンテンツを表すフィールドを定義する。

ポイント:
- コンテンツを表すフィールド名には`body`を指定する
- デフォルトのフィールド名を変更する場合は:ref:`data_format-xml_content_name_change`を参照

フォーマット定義ファイル:

```bash
file-type:        "XML"
text-encoding:    "UTF-8"

[parent]
1 child   OB

[child]
1 @attr   X
2 body    X
```

対応XMLデータ:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<parent>
  <child attr="value1">value2</child>
</parent>
```

Mapデータ:

```java
Map<String, Object> data = new HashMap<String, Object>();
data.put("child.attr", "value1");
data.put("child.body", "value2");
```

## 文字の置き換え(寄せ字)を行う

寄せ字機能を使うことで、外部からデータを読み込む際にシステムで使用可能な文字に置き換えられる。

**置き換えルール**:
- propertiesファイルに「置き換え前の文字=置き換え後の文字」形式で定義
- 置き換え前・後ともに1文字のみ（サロゲートペア非対応）
- 接続先ごとに複数のpropertiesファイルを作成可能

```properties
髙=高
﨑=崎
唖=■
```

`CharacterReplacementManager`をコンポーネント名`characterReplacementManager`で設定し、`CharacterReplacementConfig`をリスト形式で指定する。複数propertiesファイルを定義する場合は`typeName`に異なる名前を設定する。

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

初期化対象リストへの設定:

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

フォーマット定義ファイルで:ref:`data_format-replacement_convertor`コンバータを使用:

```bash
# Aシステムとの置き換えルールを適用
1 name N(100) replacement("a_system")

# Bシステムとの置き換えルールを適用
1 name N(100) replacement("b_system")
```

## 出力するデータの表示形式をフォーマットする

データを出力する際に:ref:`format`コンバータを使用することで、日付や数値などのデータの表示形式をフォーマットできる。詳細は:ref:`format`を参照。
