**結論**: バッチのリクエスト単体テスト(`BatchRequestTestSupport` を継承)では、起動パラメータ(コマンドライン引数)をテストデータのExcelファイルのケース表(`testShots`)に **`diConfig` / `requestPath` / `userId`** の3カラムで指定します。これらはバッチ起動時のコマンドライン引数(`-diConfig` / `-requestPath` / `-userId`)に対応しています。

**根拠**:

- リクエスト単体テスト(バッチ)のテストケース表は、LIST_MAPデータタイプで `testShots` というIDで定義し、1ケース毎に以下の項目を持たせます(いずれも必須)。
  - `diConfig`: バッチを実行する際のコンポーネント設定ファイルへのパスを記載(コマンドライン引数の `-diConfig` に相当)
  - `requestPath`: バッチを実行する際のリクエストパスを記載(`-requestPath` に相当。書式は「実行するアクションのクラス名/リクエストID」)
  - `userId`: バッチ実行ユーザIDを記載(`-userId` に相当。セッションコンテキスト変数 `user.id` に格納される)
- バッチのリクエスト単体テストは、実際にバッチをコマンドラインから起動したときの動作を擬似的に再現してテストを行います。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

- テストクラスは `BatchRequestTestSupport` を継承して作成し、`testShots` に記述したテストデータを基に、フレームワークが起動パラメータを組み立ててバッチ処理を擬似実行します。

**注意点**:

- `diConfig` / `requestPath` / `userId` の3項目は必須カラムのため、省略できません。
- `requestPath` は「クラス名/リクエストID」の書式で指定する必要があります。
- Excelの `testShots` シートのIDは **`testShots`** 固定で記載します。

参照:
- `development-tools/testing-framework/testing-framework-02-requestunittest-batch.json#s5`
- `development-tools/testing-framework/testing-framework-02-requestunittest-batch.json#s17`
- `development-tools/testing-framework/testing-framework-RequestUnitTest-batch.json#s1`
- `component/handlers/handlers-main.json#s3`
