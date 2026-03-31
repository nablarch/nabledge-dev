**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストケース一覧（`testShots` シート）のカラムとして指定します。必須の起動引数（`diConfig`、`requestPath`、`userId`）はカラムとして定義し、追加の起動パラメータは `args[n]` 形式または任意カラム名で指定します。

**根拠**:

テストクラスは `BatchRequestTestSupport`（`nablarch.test.core.batch.BatchRequestTestSupport`）を継承して作成します。テストケース一覧（LIST_MAPのデータタイプ、ID: `testShots`）に以下のカラムを定義することで起動パラメータを指定します。

**必須の起動引数カラム（コマンドライン引数に対応）**:

| カラム名 | 説明 |
|---|---|
| `diConfig` | バッチ実行時のコンポーネント設定ファイルへのパス |
| `requestPath` | バッチ実行時のリクエストパス |
| `userId` | バッチ実行ユーザID |

**追加の起動パラメータの指定方法**（2種類）:

1. **位置引数（`args[n]`形式）**: バッチ起動時の引数を指定するには、`args[n]`（nは0以上の整数）形式でテストケース一覧にカラムを追加します。
   > 警告: 添字nは連続した整数でなければなりません。

2. **コマンドラインオプション形式（任意カラム名）**: `args[n]` 以外のカラムを追加すると、そのカラムはコマンドラインオプションとみなされます。例えば、`paramA` カラム（値 `valueA`）と `paramB` カラム（値 `valueB`）があれば、`-paramA=valueA -paramB=valueB` というコマンドラインオプションを指定したことになります。カラム名がオプション名、セルの値がオプション値となります。

**テストメソッドの作成例**:

```java
@Test
public void testRegisterUser() {
    execute();   // テストメソッド名をシート名として使用
}
```

テストメソッドは `@Test` アノテーションを付与し、スーパクラスの `execute()` または `execute(String sheetName)` を呼び出します。

**注意点**:
- `args[n]` の添字（n）は0以上の連続した整数でなければなりません（例: `args[0]`, `args[1]`, `args[2]`）。飛び番は不可。
- `diConfig`、`requestPath`、`userId` は必須カラムです。
- テストクラスはテスト対象Actionクラスと同一パッケージに配置し、クラス名は `{Action名}RequestTest` とします。

参照: `development-tools/testing-framework/testing-framework-batch-02_RequestUnitTest.json#s4`, `development-tools/testing-framework/testing-framework-batch-02_RequestUnitTest.json#s3`, `development-tools/testing-framework/testing-framework-batch-02_RequestUnitTest.json#s1`, `development-tools/testing-framework/testing-framework-batch.json#s7`
