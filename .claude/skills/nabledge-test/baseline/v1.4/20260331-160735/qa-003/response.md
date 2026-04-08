**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、Excelファイルのテストケース一覧（LIST_MAP=`testShots`）に専用カラムを追加します。

**根拠**:

**1. 基本的なコマンドライン引数（`diConfig`、`requestPath`、`userId`）**

テストケース一覧の以下のカラムが、バッチ起動時のコマンドライン引数に対応しています：

| カラム名 | 説明 | 必須 |
|---|---|---|
| `diConfig` | バッチ実行時のコンポーネント設定ファイルへのパス | ○ |
| `requestPath` | バッチ実行時のリクエストパス | ○ |
| `userId` | バッチ実行ユーザID | ○ |

**2. 任意の起動引数（`args[n]`）**

バッチ起動時の追加引数を指定するには、`args[n]`（nは0以上の整数）形式でカラムを追加します：

```
| no | ... | requestPath | args[0]   | args[1]   |
|---|---|---|---|---|
| 1  | ... | myBatch     | value0    | value1    |
```

> **警告**: 添字 `n` は連続した整数でなければなりません（例：`args[0]`、`args[1]`、`args[2]`）。

**3. コマンドラインオプション形式での指定**

`args[n]` 以外のカラム名を追加すると、コマンドラインオプションとして扱われます。例えば `paramA` カラムに値 `valueA`、`paramB` カラムに値 `valueB` を設定すると、`-paramA=valueA -paramB=valueB` というオプションが指定されたことになります。

**テストクラスの基本構造**:

```java
import nablarch.test.core.batch.BatchRequestTestSupport;

public class MyBatchActionRequestTest extends BatchRequestTestSupport {

    @Test
    public void testSuccess() {
        execute(); // Excelシート名 "testSuccess" を使用
    }
}
```

**注意点**:
- `args[n]` の添字は必ず連続した整数にしてください（`args[0]`, `args[1]`, `args[2]` の順）。飛び番は使用できません。
- `diConfig`、`requestPath`、`userId` は必須カラムです。
- テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承して作成します（複数シート分割の場合は `nablarch.test.core.messaging.BatchRequestTestSupport`）。

参照: `testing-framework-batch-02_RequestUnitTest.json#s4`, `testing-framework-batch-02_RequestUnitTest.json#s3`, `testing-framework-batch-02_RequestUnitTest.json#s1`