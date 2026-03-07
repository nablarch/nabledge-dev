# リクエスト単体テストの実施方法(同期応答メッセージ受信処理)

## テストクラスの書き方

テストクラス作成ルール: (1) テスト対象Actionクラスと同一パッケージ (2) クラス名は`{Action名}RequestTest` (3) `nablarch.test.core.http.MessagingRequestTestSupport`を継承

**クラス**: `nablarch.test.core.http.MessagingRequestTestSupport`

## テストメソッド分割

1テストクラスにつき1テストメソッド、1テストシートを原則とする。ケースが複雑またはデータ量が多い場合は、メソッドやシートを分割してもよい。

## テストデータの書き方

テストデータExcelファイルは、テストソースコードと同じディレクトリに同じ名前（拡張子のみ異なる）で格納する。記述方法詳細: :ref:`how_to_write_excel`

### テストクラスで共通のデータベース初期値

:ref:`request_test_setup_db` を参照。

### テストショット一覧

LIST_MAPのデータタイプで記載。IDは`testShots`固定。

| カラム名 | 説明 | 必須 |
|---|---|---|
| no | テストケース番号（1からの連番） | ○ |
| description | テストケースの説明 | ○ |
| expectedStatusCode | 期待するステータスコード | ○ |
| setUpTable | 実行前DBに登録するデータのグループID[1] | |
| expectedTable | DB比較用期待テーブルのグループID[1] | |
| expectedLog | 期待するログメッセージのID | |
| diConfig | 常駐プロセスのコンポーネント設定ファイルへのパス（:ref:`コマンドライン引数 <main-run_application>` 参照）[2] | ○ |
| requestPath | 常駐プロセスのリクエストパス（:ref:`コマンドライン引数 <main-run_application>` 参照）[2] | ○ |
| userId | 常駐プロセス実行ユーザID（:ref:`コマンドライン引数 <main-run_application>` 参照）[2] | ○ |

[1] デフォルトのグループIDを使用したい場合は`default`と記載。デフォルトと個別グループは併用可能で、両方のデータが有効になる。
[2] ここで言う「常駐プロセス」とはメッセージ送受信を行うプロセス。

## データベースの準備

オンラインと同様に、グループIDで対応付けを行う（:ref:`request_test_testcases` 参照）。

![テストショットとデータベース準備の対応](../../knowledge/development-tools/testing-framework/assets/testing-framework-real/msg_shot_to_db.png)

テストショット一覧のsetUpTable欄がない場合、または空欄の場合、データベース準備は行われない。

## リクエストメッセージ

テストの入力データとなる要求電文の記述形式:

1. 先頭行: `MESSAGE=setUpMessages`固定
2. 共通情報（ディレクティブ、フレームワーク制御ヘッダ）: key-value形式で記載。リクエストメッセージの全メッセージで共通の値となる。
3. メッセージボディ: フレームワーク制御ヘッダ以降のメッセージ

> **重要**: フレームワーク制御ヘッダの項目をPJで変更している場合、propertiesファイルに`reader.fwHeaderfields`キーでフレームワーク制御ヘッダ名をカンマ区切りで指定する必要がある。
> 
> ```properties
> # フレームワーク制御ヘッダ名をカンマ区切りで指定する。
> reader.fwHeaderfields=requestId,addHeader
> ```

メッセージボディの行構成:

| 行 | 記述内容 | 備考 |
|---|---|---|
| 1行目 | フィールド名称 | 先頭セルは"no" |
| 2行目 | データタイプ | 先頭セルは空白 |
| 3行目 | フィールド長 | 先頭セルは空白 |
| 4行目以降 | データ | 先頭セルは1からの通番 |

> **重要**: フィールド名称に重複した名称は許容されない。例えば「氏名」フィールドが2つ以上存在してはならない（「本会員氏名」「家族会員氏名」のようにユニークな名称を付与する）。

本表はテストショット一覧のnoと対応。テストショットno1の要求電文 = 本表の1行目（no 1）のデータ。

![テストショットとリクエストメッセージの対応](../../knowledge/development-tools/testing-framework/assets/testing-framework-real/msg_shot_to_req.png)

## レスポンスメッセージ

リクエストメッセージと同じ形式。名前は`MESSAGE=expectedMessages`とする。

テストデータのディレクティブに設定されたfile-typeの値によりアサート方法が変わる:

| file-typeの値 | アサート方法 |
|---|---|
| Fixed または指定なし | テストデータに記載された項目単位に電文を分割してアサート |
| その他の値 | 電文全体を文字列として扱いアサート |

> **重要**: file-typeはフォーマット定義ファイルではなく、テストデータに設定すること。

項目単位アサートのfile-typeリストは環境設定ファイルで変更可能:

```text
messaging.assertAsMapFileType=<カンマ区切りのfile-typeリスト>
```

> **補足**: XMLやJSONでは電文長が電文ごとに異なり、テストデータの内容に応じて自動計算される。実電文とテストデータの電文長が異なると正常に読み込めない場合がある。XMLやJSONを使用する場合は必ずfile-typeを設定し、電文全体を文字列としてアサートを行うこと。

## 期待するデータベースの状態

データベースの準備と同様に、期待するデータベースの状態をテストケース一覧とIDでリンクさせる（`expectedTable`カラムにグループIDを指定）。

## テストメソッドの書き方

**クラス**: `nablarch.test.core.http.MessagingRequestTestSupport`を継承する。

テストメソッド内でスーパクラスの以下のいずれかのメソッドを呼び出す:
- `void execute()` — 引数なし。テストメソッド名をシート名として`execute(テストメソッド名)`と等価
- `void execute(String sheetName)` — テストデータのシート名を指定

通常、テストシート名とテストメソッド名は同一なので、引数なしの`execute()`を使用する。

```java
@Test
public void testRegisterUser() {
    execute();   // execute("testRegisterUser") と等価
}
```

## テスト起動方法

クラス単体テストと同様。通常のJUnitテストと同じように実行する。

## テスト結果検証

自動テストフレームワーク側で以下の結果検証が行われる:

1. レスポンスメッセージの結果検証（必須）
2. データベースの結果検証
3. ログの結果検証

データベースとログの結果検証は、テストショット一覧に期待値の記載がない場合（空欄）はスキップされる。
