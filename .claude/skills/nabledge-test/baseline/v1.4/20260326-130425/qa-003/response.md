**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、Excelファイルのテストケース一覧（`LIST_MAP=testShots`）に専用カラムを追加します。

**根拠**:

**必須の起動パラメータ（全テストケースで必要）**

テストケース一覧には以下3つのカラムが必須です（`about_commandline_argument` 参照）：

| カラム名 | 説明 |
|---|---|
| `diConfig` | バッチ実行時のコンポーネント設定ファイルへのパス |
| `requestPath` | バッチ実行時のリクエストパス |
| `userId` | バッチ実行ユーザID |

**コマンドライン引数（位置引数）の指定方法**

位置引数（`-キー=値` 形式でない引数）を指定するには、`args[n]`（nは0以上の整数）形式でカラムを追加します。

> **警告**: 添字nは連続した整数でなければなりません（`args[0]`, `args[1]`, `args[2]`, ...）。

**コマンドラインオプション引数の指定方法**

`args[n]` 以外のカラム名を追加すると、そのカラムはコマンドラインオプションとみなされます。例えば、テストケース一覧に `paramA` カラム（値 `valueA`）と `paramB` カラム（値 `valueB`）を追加すると、`-paramA=valueA -paramB=valueB` というコマンドラインオプションを指定したことになります。カラム名がオプション名、セルの値がオプション値になります。

**テストケース一覧の例（testShots）**:

| no | description | expectedStatusCode | diConfig | requestPath | userId | args[0] | paramA |
|---|---|---|---|---|---|---|---|
| 1 | 正常 | 100 | batch-component-configuration.xml | ss11AC.B11AC011Action/RB11AC0110 | batch_user | file_input.csv | valueA |

**テストクラスの実装**:

```java
import nablarch.test.core.batch.BatchRequestTestSupport;

public class B11AC011ActionRequestTest extends BatchRequestTestSupport {
    @Test
    public void testSuccess() {
        execute();
    }
}
```

**注意点**:
- `args[n]` の添字nは連続した整数でなければなりません（`args[0]`, `args[1]`, ... の順）。飛び番は不可。
- `diConfig`, `requestPath`, `userId` の3カラムは必須です。
- `args[n]` と追加カラム（オプション引数）は組み合わせて使用できます。
- 実際のバッチ起動コマンド（`nablarch.fw.launcher.Main`）では、コマンドライン引数は `-キー名=値` 形式（オプション）または単純値（引数）として解釈されます。

参照: `testing-framework-batch-02_RequestUnitTest.json#s4`, `testing-framework-batch-02_RequestUnitTest.json#s3`, `nablarch-batch-5.json#s1`, `nablarch-batch-02_basic.json#s5`
