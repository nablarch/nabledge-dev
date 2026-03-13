**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストケース一覧（`testShots`）に `args[n]`（nは0以上の整数）形式のカラムを追加します。また、標準カラム以外のカラムはコマンドラインオプションとして扱われます。

**根拠**:

**① `args[n]` 形式による起動引数の指定**

バッチ起動時の引数は `args[n]`（nは0以上の整数）形式でテストケース一覧にカラムを追加します。

> **重要**: 添字nは連続した整数でなければなりません（例: `args[0]`, `args[1]`, `args[2]`）。

**② コマンドラインオプションの指定**

テストケース一覧の標準カラム以外のカラムはコマンドラインオプションとみなされます。
例: カラム名 `paramA` に値 `valueA` を設定すると、`-paramA=valueA` として扱われます。

**③ テストケース一覧（`testShots`）の標準カラム構成**

テストケース一覧は LIST_MAP データタイプで記述し、IDは `testShots` とします。主な必須カラムは以下のとおりです:

| カラム名 | 説明 | 必須 |
|---|---|---|
| no | テストケース番号（1からの連番） | ○ |
| description | テストケースの説明 | ○ |
| expectedStatusCode | 期待するステータスコード | ○ |
| diConfig | バッチ実行時のコンポーネント設定ファイルパス | ○ |
| requestPath | バッチ実行時のリクエストパス | ○ |
| userId | バッチ実行ユーザID | ○ |
| args[n] | バッチ起動引数（nは0以上の連続した整数） | |

**④ テストクラスの作成**

テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承して作成します。クラス名は `{ActionクラスのAction名}RequestTest` とします。

```java
package nablarch.sample.ss21AC01;

import nablarch.test.core.batch.BatchRequestTestSupport;

public class B21AC01Test extends BatchRequestTestSupport {
    // テストメソッドを実装
}
```

**注意点**:
- `args[n]` の添字 n は **連続した整数** でなければなりません（飛び番不可）。
- 標準カラム以外のカラムはコマンドラインオプション（`-カラム名=値` 形式）として扱われるため、カラム名の命名には注意が必要です。
- `diConfig`、`requestPath`、`userId` は必須カラムです。

参照: `development-tools/testing-framework/testing-framework-batch-02_RequestUnitTest.json#s4`, `development-tools/testing-framework/testing-framework-batch-02_RequestUnitTest.json#s3`, `development-tools/testing-framework/testing-framework-batch-02_RequestUnitTest.json#s1`
