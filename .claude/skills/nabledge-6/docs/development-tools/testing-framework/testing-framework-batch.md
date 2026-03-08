# リクエスト単体テストの実施方法(バッチ)

## テストクラスの書き方

テストクラス作成ルール: (1) テスト対象Actionクラスと同一パッケージ (2) クラス名は`{Actionクラス名}RequestTest` (3) **クラス**: `nablarch.test.core.batch.BatchRequestTestSupport`を継承する。

## テストメソッド分割

原則1テストケース1テストメソッド。以下の場合は複数テストケースを1テストメソッドにまとめることを検討する:
- テストケース間の関連が強く、シート分割により可読性が劣化する場合（例：入力ファイルのフォーマットチェック）
- テストデータが少量で、1シートに記述しても可読性・保守性に影響しない場合

## テストデータの書き方

テストデータExcelファイルはテストソースコードと同じディレクトリに同名（拡張子のみ異なる）で格納する。書式詳細は :ref:`how_to_write_excel` を参照。

テストクラスで共通のデータベース初期値: :ref:`request_test_setup_db` を参照。

**テストケース一覧**: LIST_MAPデータタイプで記述し、IDは`testShots`とする。

| カラム名 | 説明 | 必須 |
|---|---|---|
| no | テストケース番号（1からの連番） | ○ |
| description | テストケースの説明 | ○ |
| expectedStatusCode | 期待するステータスコード | ○ |
| setUpTable | テスト前にDBへ登録するデータの :ref:`グループID<tips_groupId>` | |
| setUpFile | テスト前に入力ファイルを作成するデータの :ref:`グループID<tips_groupId>` | |
| expectedFile | 出力ファイル比較の期待データの :ref:`グループID<tips_groupId>` | |
| expectedTable | DB比較の期待テーブルの :ref:`グループID<tips_groupId>` | |
| expectedLog | 期待するログメッセージを記載したLIST_MAP ID（ログ出力の自動検証に使用） | |
| diConfig | バッチ実行時のコンポーネント設定ファイルパス（ :ref:`main-run_application` 参照） | ○ |
| requestPath | バッチ実行時のリクエストパス（ :ref:`main-run_application` 参照） | ○ |
| userId | バッチ実行ユーザID（ :ref:`main-run_application` 参照） | ○ |
| expectedMessage | メッセージ同期送信処理の期待要求電文の :ref:`グループID<tips_groupId>` | |
| responseMessage | メッセージ同期送信処理の返却応答電文の :ref:`グループID<tips_groupId>` | |
| expectedMessageByClient | HTTPメッセージ同期送信処理の期待要求電文の :ref:`グループID<tips_groupId>` | |
| responseMessageByClient | HTTPメッセージ同期送信処理の返却応答電文の :ref:`グループID<tips_groupId>` | |

> **補足**: グループIDに`default`と記載するとデフォルトグループIDを使用できる。デフォルトと個別グループは併用可能（両方のデータが有効になる）。

## コマンドライン引数

バッチ起動時の引数は`args[n]`（nは0以上の整数）形式でテストケース一覧にカラムを追加する。

> **重要**: 添字nは連続した整数でなければならない。

テストケース一覧の標準カラム以外のカラムはコマンドラインオプションとみなされる。例: カラム名`paramA`に値`valueA`を設定すると`-paramA=valueA`として扱われる。

## データベースの準備

:ref:`request_test_testcases`（オンライン）と同様に、グループIDで対応付けを行う。

## 固定長ファイルの準備

テストデータに固定長ファイルのデータを記載すると、テスト実行前にフレームワークが自動でファイルを作成する。

**書式**: `SETUP_FIXED[グループID]=ファイルパス`

| 名称 | 説明 |
|---|---|
| グループID | テストケース一覧の`setUpFile`に記載したグループIDと対応する |
| ファイルパス | カレントディレクトリからのファイルパス（ファイル名含む） |
| ディレクティブ行 | `text-encoding`・`record-separator`等を指定。`file-type`と`record-length`は不要（SETUP_FIXED指定で固定長を表し、フィールド長からパディングサイズを決定するため） |
| レコード種別 | レコード種別名（マルチレイアウトの場合は連続で記載） |
| フィールド名称 | フィールドごとに記載 |
| データ型 | 日本語名称で記載（例：半角英字）。マッピングは[BasicDataTypeMapping](https://github.com/nablarch/nablarch-testing/blob/main/src/main/java/nablarch/test/core/file/BasicDataTypeMapping.java)のDEFAULT_TABLEを参照 |
| フィールド長 | フィールドごとに記載 |
| データ | フィールドに格納する値。複数レコードは次行に続けて記載 |

> **重要**: 1レコード種別内でフィールド名称の重複は不可（例：「氏名」フィールドが2つ以上存在してはならない）。異なるレコード種別間での同一名称は問題なし。

> **補足**: フィールド名称・データ型・フィールド長は外部インタフェース設計書から「**行列を入れ替える**」オプションでコピー＆ペーストすることで効率良く作成できる。

> **補足**: 「符号無数値」「符号付数値」データ型使用時は、固定長ファイル上の実際の値（パディング文字・符号を含む）をそのまま記載する。これらを使用する場合はテスト用データタイプの設定が必要。デフォルト設定を省略するとデフォルト設定が上書きされるため、既存のデフォルトエントリも必ず含めること。

```xml
<component name="fixedLengthConvertorSetting"
    class="nablarch.core.dataformat.convertor.FixedLengthConvertorSetting">
  <property name="convertorTable">
    <map>
      <!-- デフォルトの設定（省略不可） -->
      <entry key="X" value="nablarch.core.dataformat.convertor.datatype.SingleByteCharacterString"/>
      <entry key="N" value="nablarch.core.dataformat.convertor.datatype.DoubleByteCharacterString"/>
      <entry key="XN" value="nablarch.core.dataformat.convertor.datatype.ByteStreamDataString"/>
      <entry key="Z" value="nablarch.core.dataformat.convertor.datatype.ZonedDecimal"/>
      <entry key="SZ" value="nablarch.core.dataformat.convertor.datatype.SignedZonedDecimal"/>
      <entry key="P" value="nablarch.core.dataformat.convertor.datatype.PackedDecimal"/>
      <entry key="SP" value="nablarch.core.dataformat.convertor.datatype.SignedPackedDecimal"/>
      <entry key="B" value="nablarch.core.dataformat.convertor.datatype.Bytes"/>
      <entry key="X9" value="nablarch.core.dataformat.convertor.datatype.NumberStringDecimal"/>
      <entry key="SX9" value="nablarch.core.dataformat.convertor.datatype.SignedNumberStringDecimal"/>
      <entry key="pad" value="nablarch.core.dataformat.convertor.value.Padding"/>
      <entry key="encoding" value="nablarch.core.dataformat.convertor.value.UseEncoding"/>
      <entry key="_LITERAL_" value="nablarch.core.dataformat.convertor.value.DefaultValue"/>
      <entry key="number" value="nablarch.core.dataformat.convertor.value.NumberString"/>
      <entry key="signed_number" value="nablarch.core.dataformat.convertor.value.SignedNumberString"/>
      <!-- テスト用: 符号無数値(X9)→TEST_X9, 符号有数値(SX9)→TEST_SX9 -->
      <entry key="TEST_X9" value="nablarch.test.core.file.StringDataType"/>
      <entry key="TEST_SX9" value="nablarch.test.core.file.StringDataType"/>
    </map>
  </property>
</component>
```

## テストクラスの作成ルールと分割方針

テストクラス作成ルール: (1) パッケージはテスト対象取引のパッケージ (2) クラス名は`{取引ID}Test` (3) `BatchRequestTestSupport`を継承

テストケース分割の基本方針: 1シートにつき1テストケース

**クラス**: `nablarch.test.core.batch.BatchRequestTestSupport`

```java
package nablarch.sample.ss21AC01;
import nablarch.test.core.batch.BatchRequestTestSupport;

public class B21AC01Test extends BatchRequestTestSupport {
```

## 複雑なテストケースの場合

テストデータが大量または1取引に含まれる処理が多い場合、1シートに全テストデータを詰め込むと可読性が低下する。このような場合は1ケースを複数シートに分割して記述してもよい。

## 非常に簡単なテストケースの場合

非常に簡単なテストケースでテストデータ量が少ない場合、1シートに全テストケースを含めてもよい。

## 基本的な記述方法

`execute()` でテストを実行する。シートは `LIST_MAP=testShots` 形式で記述する。

```java
@Test
public void testSuccess() {
    execute();
}
```

testShotsの列: `no`, `description`, `expectedStatusCode`, `setUpTable`, `setUpFile`, `expectedTable`, `expectedFile`, `requestPath`

## 1テストケースを複数シートに分割する場合

`execute("シート名")` でシートを指定してバッチを実行できる。各シートは独立した `LIST_MAP=testShots` を持つ。

```java
@Test
public void testSuccess() {
    execute("testSuccess_fileInput");
    execute("testSuccess_userDelete");
    execute("testSuccess_fileOutput");
}
```

## 1シートに複数ケースを含める場合

noを`1-1`,`1-2`,`2-1`,`2-2`のように番号でグループ化することで、1シートに複数テストケースのデータを記述できる。

> **補足**: グループIDを使用することで1シートに複数ケースのテストデータを記述できる。詳細は :ref:`tips_groupId` を参照。

## 可変長ファイル（CSVファイル）の準備

可変長ファイル（CSVファイル）の準備は固定長とほぼ同様。**固定長との違い**: フィールド長を記載しない。

テストシートでの定義例:

`SETUP_VARIABLE=work/members.csv`

| 区分 | フィールド1 | フィールド2 | フィールド3 |
|---|---|---|---|
| text-encoding | Windows-31J | | |
| record-separator | CRLF | | |
| ヘッダ | レコード区分 | | |
| | 半角数字 | | |
| | 0 | | |
| データ | レコード区分 | 会員番号 | 入会日 |
| | 半角数字 | 半角数字 | 半角数字 |
| | 1 | 0000000001 | 20100101 |
| | 1 | 0000000002 | 20100102 |
| トレーラ | レコード区分 | レコード件数 | |
| | 半角数字 | 数値 | |
| | 8 | 2 | |
| エンド | レコード区分 | | |
| | 半角数字 | | |
| | 9 | | |

> **補足**: フィールド区切り文字を変更する場合、ディレクティブで明示的に指定する。例：タブ区切り（TSV）にする場合: `field-separator=\t`

## 空のファイルを定義する方法

空のファイル（0バイト）を定義するには、ディレクティブ行を定義しレコードの定義を省略する。

`SETUP_VARIABLE=work/members.csv`

| | |
|---|---|
| text-encoding | Windows-31J |
| record-separator | CRLF |
| //空ファイル | |

## 期待するデータベースの状態

:ref:`オンライン<request_test_expected_tables>` と同様に、期待するデータベースの状態をテストケース一覧とリンクさせる。テストケース一覧の `expectedTable` 欄にグループIDを記載することで、そのグループIDのテストデータで実際のDB状態を確認できる。

## 期待する固定長ファイル

テスト対象バッチが出力する固定長ファイルをアサートする。準備データのデータタイプ `SETUP_FIXED` に対し、期待値では `EXPECTED_FIXED` を使用する。その他の記述方法は`固定長ファイルの準備`_と同様。

## 期待する可変長ファイル

テスト対象バッチが出力する可変長ファイルをアサートする。準備データのデータタイプ `SETUP_VARIABLE` に対し、期待値では `EXPECTED_VARIABLE` を使用する。その他の記述方法は`可変長ファイル（CSVファイル）の準備`_と同様。

## テストメソッドの書き方

**クラス**: `BatchRequestTestSupport` を継承する。

テストメソッド内でスーパクラスの以下のいずれかのメソッドを呼び出す:
- `void execute()` - 引数なし（テストデータのシート名にテストメソッド名を指定したのと同じ動作）
- `void execute(String sheetName)` - テストデータのシート名を明示指定

通常は `execute()` を使用する。引数なしの場合、テストデータのシート名にテストメソッド名を指定したのと同じ動作となる。

```java
@Test
public void testResigster() {
    execute();   // execute("testRegisterUser") と等価
}
```

## テスト起動方法

クラス単体テストと同様に、通常のJUnitテストと同じように実行する。

## テスト結果検証

### データベースの結果検証

テストケース一覧の `expectedTable` 欄にグループIDを記載することで、そのグループIDのテストデータで実際のDB状態を確認できる。

### ファイルの結果検証

テストケース一覧の `expectedFile` 欄にグループIDを記載することで確認できる。

| ファイル種別 | グループID指定なし | グループID指定あり |
|---|---|---|
| 固定長ファイル | `EXPECTED_FIXED=比較対象ファイルのパス` | `EXPECTED_FIXED[グループID]=比較対象ファイルのパス` |
| 可変長ファイル | `EXPECTED_VARIABLE=比較対象ファイルのパス` | `EXPECTED_VARIABLE[グループID]=比較対象ファイルのパス` |

### ログの結果検証

テストケース一覧の `expectedLog` 欄にグループIDを記載することで確認できる。

`LIST_MAP=expectedLogMessages` に以下のカラムを定義:

| カラム名 | 内容 |
|---|---|
| logLevel | 期待するログのログレベル |
| message**N**（Nは1以上の整数） | 期待するログに含まれる文言（複数指定可、連続した値であること） |

> **補足**: logLevel と全messageN の条件は**AND**条件。logLevelが不一致の場合、または期待する文言が1つでもログ出力されていない場合、期待ログとは見なされない。

> **重要**: `expectedLog` 欄にグループIDを記載した場合、必ず期待するメッセージを1行以上設定すること。メッセージが0行の場合、またはグループIDに紐付くLIST_MAP要素が存在しない場合、フレームワークは例外を送出する。
