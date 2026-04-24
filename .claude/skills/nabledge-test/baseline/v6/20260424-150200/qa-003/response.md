**結論**: バッチのリクエスト単体テスト（`BatchRequestTestSupport` を継承したテストクラス）で起動パラメータ（コマンドライン引数）を指定するには、Excel テストデータのテストケース一覧（LIST_MAP=testShots）に **`args[n]`**（n は 0 以上の連続した整数）カラムを追加します。`args[n]` 以外のカラムを追加すると、そのカラムは **コマンドラインオプション** （`-カラム名=値` 形式）として扱われます。また、必須カラムとして `diConfig`（コンポーネント設定ファイルパス）、`requestPath`（リクエストパス）、`userId`（バッチ実行ユーザID）も指定する必要があります。

**根拠**:

1. コマンドライン引数（args）の指定方法（`testing-framework-02-requestunittest-batch.json#s6`）:

   ```
   | no | case | ... | args[0] | args[1] | args[2] |
   |----|------|-----|---------|---------|---------|
   | 1  | xxxのケース | ... | 第1引数 | 第2引数 | 第3引数 |
   ```

   > 添字nは連続した整数でなければならない。

2. コマンドラインオプション（`-name=value`）の指定方法（同 s6）:

   ```
   | no | case | ... | paramA | paramB |
   |----|------|-----|--------|--------|
   | 1  | xxxのケース | ... | valueA | valueB |
   ```
   → 実行時に `-paramA=valueA -paramB=valueB` が指定されたことになる。

3. testShots の必須カラム（`testing-framework-02-requestunittest-batch.json#s5`）:
   - `diConfig`: バッチ実行時のコンポーネント設定ファイルへのパス（必須）
   - `requestPath`: バッチ実行時のリクエストパス（必須）
   - `userId`: バッチ実行ユーザID（必須）
   - `expectedStatusCode`: 期待するステータスコード（必須）

4. テストクラス作成例（`testing-framework-02-requestunittest-batch.json#s1`）:

   ```java
   public class RM21AA001ActionRequestTest extends BatchRequestTestSupport {
   }
   ```

   テストメソッドでは `execute()` もしくは `execute(String sheetName)` を呼び出します（同 s19）。

**注意点**:
- `args[n]` の添字 n は **連続した整数** でなければなりません（欠番不可）。
- `args[n]` 以外のカラムを testShots に追加すると、すべてコマンドラインオプションとみなされるため、予期しないカラムを含めないよう注意が必要です。
- `diConfig`、`requestPath`、`userId` は testShots の必須カラムです（詳細は `handlers-main.md#main-run-application` のコマンドライン引数仕様を参照）。

参照:
- `testing-framework-02-requestunittest-batch.json#s6`（コマンドライン引数/オプションの指定）
- `testing-framework-02-requestunittest-batch.json#s5`（testShots の必須カラム）
- `testing-framework-02-requestunittest-batch.json#s1`（テストクラス作成ルール）
- `testing-framework-02-requestunittest-batch.json#s19`（execute メソッド）
- `testing-framework-RequestUnitTest-batch.json#s7`（BatchRequestTestSupport 概要）
