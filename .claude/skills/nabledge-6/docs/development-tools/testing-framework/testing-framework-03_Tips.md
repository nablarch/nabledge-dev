# 目的別API使用方法

## Excelファイルから、入力パラメータや戻り値に対する期待値などを取得したい

データタイプ`LIST_MAP=<ID>`を使用してExcelファイルからList<Map<String,String>>形式のデータを取得できる。

- データ2行目: MapのKey
- データ3行目以降: MapのValue

**メソッド**: `TestSupport#getListMap(String sheetName, String id)`, `DbAccessTestSupport#getListMap(String sheetName, String id)`（第1引数: シート名、第2引数: ID）

```java
List<Map<String, String>> parameters = getListMap("testGetName", "parameters");
Map<String, String> param = parameters.get(0);
String empNo = param.get("empNo");
String expected = param.get("expected");
```

Excelシート記述形式（`LIST_MAP=parameters`）:

| empNo | expected |
|---|---|
| 00001 | 山田太郎 |
| 00002 | 鈴木一郎 |

## 同じテストメソッドをテストデータを変えて実行したい

List-Mapで取得したデータをループしてテストを実行することで、Excelデータを追加するだけでデータバリエーションを増やせる。

```java
List<Map<String, String>> parameters = getListMap("testGetName", "parameters");
for (Map<String, String> param : parameters) {
    String empNo = param.get("empNo");
    String expectedDataId = param.get("expectedDataId");
    SqlResultSet actual = target.selectByPk(empNo);
    assertSqlResultSetEquals("testSelectByPk", expectedDataId, actual);
}
```

> **重要**: 更新系のテストを行う場合、ループ内で`setUpDb`を呼び出すこと。そうしないとテストの成否がデータの順番に依存する。

## 一つのシートに複数テストケースのデータを記載したい

グループIDを付与することで、`EXPECTED_TABLE`と`SETUP_TABLE`の複数テストケースのデータを1シートに混在させることができる。

**サポートデータタイプ**: `EXPECTED_TABLE`, `SETUP_TABLE`

書式: `データタイプ[グループID]=テーブル名`

```java
// グループID "case_001" のデータのみ登録
setUpDb("testUpdate", "case_001");
// グループID "case_001" のデータのみassert
assertTableEquals("データベース更新結果確認", "testUpdate", "case_001");
```

Excel記述例:
```
SETUP_TABLE[case_001]=EMPLOYEE_TABLE
EXPECTED_TABLE[case_001]=EMPLOYEE_TABLE

SETUP_TABLE[case_002]=EMPLOYEE_TABLE
EXPECTED_TABLE[case_002]=EMPLOYEE_TABLE
```

> **注意**: 複数グループIDのデータを記述する際は、:ref:`auto-test-framework_multi-datatype` のようにグループIDごとにまとめて記述すること。まとめて記述しないとデータ読み込みが途中で終了しテストが正しく実行されない。

## システム日時を任意の値に固定したい

**クラス**: `nablarch.test.FixedSystemTimeProvider`

コンポーネント設定ファイルの`systemTimeProvider`に`FixedSystemTimeProvider`を指定することで、任意のシステム日時を固定できる。

| プロパティ名 | 設定内容 |
|---|---|
| fixedDate | 固定日時文字列。形式: `yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁） |

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

```java
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

## シーケンスオブジェクトを使った採番のテストをしたい

シーケンスオブジェクト採番は次に採番される値が予測不可なため、テスト用設定ファイルでテーブル採番（`nablarch.common.idgenerator.FastTableIdGenerator`）に置き換えることで期待値を設定できる。

手順:
1. 採番テーブルに準備データをセットアップ
2. 期待値は「準備データの値 + 採番回数」で設定

**テスト用設定（本番の`idGenerator`コンポーネントを上書き）**:

```xml
<component name="idGenerator" class="nablarch.common.idgenerator.FastTableIdGenerator">
    <property name="tableName" value="TEST_SBN_TBL"/>
    <property name="idColumnName" value="ID_COL"/>
    <property name="noColumnName" value="NO_COL"/>
    <property name="dbTransactionManager" ref="dbTransactionManager"/>
</component>
```

> **補足**: テーブル採番用の設定値の詳細は、`IdGenerator` を参照すること。

**Excelファイル記述例（採番対象ID:1101）**:

準備データ（`SETUP_TABLE=TEST_SBN_TBL`）:

| ID_COL | NO_COL |
|--------|--------|
| 1101 | 100 |

> **補足**: 採番用テーブルには、テスト範囲内で使用する採番対象のレコードのみを設定する。

期待値（`EXPECTED_TABLE=TEST_SBN_TBL`）:

| ID_COL | NO_COL |
|--------|--------|
| 1101 | 101 |

期待値（`EXPECTED_TABLE=USER_INFO`、採番した値が登録されるテーブル）:

| USER_ID | KANJI_NAME | KANA_NAME |
|------------|------------|----------|
| 0000000101 | 漢字名 | ｶﾅﾒｲ |

> **補足**: 1度のみ採番処理が行われる場合、期待値は「準備データの値 + 1」となる。

## ThreadContextにユーザID、リクエストIDなどを設定したい

データベースアクセスクラスの自動テストでは、フレームワークを経由せず直接起動するためThreadContextに値が設定されていない。ExcelファイルにLIST_MAPでデータを記述し、以下のメソッドを呼び出すことでThreadContextに値を設定できる。

- `TestSupport#setThreadContextValues(String sheetName, String id)`
- `DbAccessTestSupport#setThreadContextValues(String sheetName, String id)`

> **補足**: 自動設定項目を使用してDBを登録・更新する際は、ThreadContextにリクエストIDとユーザIDが必要。テスト対象クラス起動前にこれらの値をThreadContextに設定すること。

**テストコード例**:

```java
setThreadContextValues("testSelect", "threadContext");
```

**Excelデータ記述例**（シート[testInsert]、`LIST_MAP=threadContext`）:

| USER_ID | REQUEST_ID | LANG |
|---------|------------|------|
| U00001 | RS000001 | ja_JP |

## 任意のディレクトリのExcelファイルを読み込みたい

別ディレクトリのExcelファイルを読み込む場合は、`TestDataParser`実装クラスを直接使用する。

```java
TestDataParser parser = (TestDataParser) SystemRepository.getObject("testDataParser");
List<Map<String, String>> list = parser.getListMap("/foo/bar/Baz.xlsx", "sheet001", "params");
```

## テスト実行前後に共通処理を行いたい

JUnit4の`@Before`、`@After`、`@BeforeClass`、`@AfterClass`アノテーションを使用することで、テスト実行前後に共通処理を実行できる。

## @BeforeClass, @AfterClass使用時の注意点

サブクラスにてスーパークラスと同名・同アノテーション（`@BeforeClass`/`@AfterClass`）のメソッドを作成しないこと。同名メソッドに同種のアノテーションを付与した場合、スーパークラスのメソッドは起動されなくなる。

```java
public class TestSuper {
    @BeforeClass
    public static void setUpBeforeClass() {
        System.out.println("super");   // 表示されない
    }
}

public class TestSub extends TestSuper {
    @BeforeClass
    public static void setUpBeforeClass() {
        // スーパークラスのメソッドを上書き
    }

    @Test
    public void test() {
        System.out.println("test");
    }
}
```

上記TestSubを実行した場合、「test」のみ表示される。

## デフォルト以外のトランザクションを使用したい

`DbAccessTestSupport`を継承することで、スーパークラスの`@Before`/`@After`メソッドが自動的に呼び出され、テストメソッド実行前後のトランザクション開始/終了が自動化される。プロパティファイルにトランザクション名を記載することで、テスティングフレームワークがトランザクション制御を行う。これにより、個別テストでの明示的なトランザクション開始や、終了処理漏れがなくなる。

## 本フレームワークのクラスを継承せずに使用したい

フレームワークのスーパークラスを継承できない場合、スーパークラスをインスタンス化して処理を委譲することで代替できる。

- コンストラクタにテストクラス自身の`Class`インスタンス（`getClass()`）を渡す必要がある
- `@Before`/`@After`メソッドは明示的に呼び出す必要がある（`beginTransactions()`/`endTransactions()`）

```java
public class SampleTest extends AnotherSuperClass {

    private DbAccessTestSupport dbSupport
          = new DbAccessTestSupport(getClass());

    @Before
    public void setUp() {
        dbSupport.beginTransactions();
    }

    @After
    public void tearDown() {
        dbSupport.endTransactions();
    }

    @Test
    public void test() {
        dbSupport.setUpDb("test");
        dbSupport.assertSqlResultSetEquals("test", "id", actual);
    }
}
```

## クラスのプロパティを検証したい

クラスのプロパティ検証にはExcelファイルのデータと照合する以下のメソッドを使用する。引数: 第1引数=エラー時メッセージ、第2引数=シート名、第3引数=ID、第4引数=検証対象（Object/Object[]/List<?>）。

- `HttpRequestTestSupport#assertObjectPropertyEquals(String message, String sheetName, String id, Object actual)`
- `HttpRequestTestSupport#assertObjectArrayPropertyEquals(String message, String sheetName, String id, Object[] actual)`
- `HttpRequestTestSupport#assertObjectListPropertyEquals(String message, String sheetName, String id, List<?> actual)`

テストデータの記述方法は :ref:`how_to_get_data_from_excel` と同様。2行目がプロパティ名、3行目以降が検証値。

**テストコード例**:

```java
assertObjectPropertyEquals(message, sheetName, "expectedUsers", users);
```

**Excelデータ記述例**（`LIST_MAP=expectedUsers`）:

| kanjiName | kanaName | mailAddress |
|-----------|----------|-------------|
| 漢字氏名 | カナシメイ | test@anydomain.com |

## テストデータに空白、空文字、改行やnullを記述したい

:ref:`special_notation_in_cell` を参照。

## テストデータに空行を記述したい

全くの空行は無視されるため、:ref:`special_notation_in_cell` のダブルクォーテーション記法（`""`）で空文字列を記述することで空行を表現できる。

> **補足**: 行のうち1セルだけ `""` にすれば良い。可読性のため左端のセルへの記載を推奨する。

**記述例**（2レコード目が空行、`SETUP_VARIABLE=/path/to/file.csv`）:

| name | address |
|------|---------|
| 山田 | 東京都 |
| "" | |
| 田中 | 大阪府 |

## マスタデータを変更してテストを行いたい

[04_MasterDataRestore](testing-framework-04_MasterDataRestore.md) を参照。

## テストデータ読み込みディレクトリを変更したい

テストデータはデフォルトで `test/java` 配下から読み込まれる。コンポーネント設定ファイルに以下のキーを追加することで変更できる。

| キー | 値 |
|---|---|
| nablarch.test.resource-root | テスト実行時のカレントディレクトリからの相対パス。セミコロン(;)区切りで複数指定可 |

```bash
nablarch.test.resource-root=path/to/test-data-dir
```

複数ディレクトリ指定例:

```text
nablarch.test.resource-root=test/online;test/batch
```

- 一時的な変更はVM引数で代替可能: `-Dnablarch.test.resource-root=path/to/test-data-dir`
- 複数ディレクトリで同名テストデータが存在する場合、最初に発見されたテストデータが読み込まれる

## メッセージング処理でテストデータに対し定型的な変換処理を追加したい

**インタフェース**: `nablarch.test.core.file.TestDataConverter`

上記インタフェースを実装しシステムリポジトリに登録することで、URLエンコーディング等の定型変換処理を追加できる。

| キー | 値 |
|---|---|
| TestDataConverter_<データ種別> | TestDataConverterを実装したクラスのクラス名。データ種別はテストデータのfile-typeに指定した値 |

```xml
<component name="TestDataConverter_FormUrlEncoded"
           class="please.change.me.test.core.file.FormUrlEncodedTestDataConverter"/>
```

![URLエンコーディング変換前のExcelファイル記述例](../../knowledge/development-tools/testing-framework/assets/testing-framework-03_Tips/data_convert_example.png)

![URLエンコーディング変換後（テストフレームワーク内部での扱い）](../../knowledge/development-tools/testing-framework/assets/testing-framework-03_Tips/data_convert_internal.png)
