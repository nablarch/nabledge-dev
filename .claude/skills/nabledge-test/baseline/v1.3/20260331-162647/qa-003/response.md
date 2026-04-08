**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストデータExcelファイルの `testShots` シートに `requestPath` 列（および必要に応じて `userId` 列）を追加して指定します。`BatchRequestTestSupport` を継承したテストクラスが、このExcelの値を読み取ってバッチ起動パラメータとして使用します。

**根拠**:

テストクラスは `BatchRequestTestSupport` を継承して作成します。

```java
package nablarch.sample.ss21AC01;
import nablarch.test.core.batch.BatchRequestTestSupport;
public class B21AC01Test extends BatchRequestTestSupport {
    @Test
    public void testSuccess() {
        execute();
    }
}
```

テストデータExcelファイルの `LIST_MAP=testShots` シートに `requestPath` 列を追加し、各テストショットの起動パラメータを指定します。

| no | description | expectedStatusCode | setUpTable | setUpFile | expectedTable | expectedFile | requestPath |
|---|---|---|---|---|---|---|---|
| 1 | ファイル入力 | 100 | default | default | default | | fileInputBatch |
| 2 | ユーザ削除 | 100 | default | | default | | userDeleteBatch |
| 3 | ファイル出力 | 100 | default | | fileInputBatch | default | fileOutputBatch |

`requestPath` は実際のバッチ起動コマンドの `-requestPath` オプションに対応し、以下の形式で指定します。

```
(業務アクションクラス名) + "/" + (リクエストID)
```

実際のコマンドライン起動との対応（参考）:

```bash
java nablarch.fw.launcher.Main \
    -diConfig=file:./config/batch-config.xml \
    -requestPath=ss11AC.B11AC011Action/RB11AC0110 \
    -userId=batch_user
```

バッチ起動に必要な必須パラメータ:

| パラメータ | 内容 |
|---|---|
| `-diConfig` | リポジトリの設定ファイルパス |
| `-requestPath` | `(アクションクラス名)/(リクエストID)` 形式 |
| `-userId` | 実行ユーザID |

**注意点**:
- `-diConfig`、`-requestPath`、`-userId` の3つは必須パラメータで、いずれかが欠けると終了コード127で異常終了します。
- テストクラスのパッケージはテスト対象取引と同一にし、クラス名は `<取引ID>Test` 形式にします（例: `B21AC01Test`）。
- 原則として1シート1テストケースで記述します。テストデータが大量な場合は複数シートへの分割も可能です。

参照: `testing-framework-batch.json#s1`, `testing-framework-batch.json#s2`, `component/handlers/handlers-Main.json#s3`, `guide/nablarch-batch/nablarch-batch-02_basic.json#s5`
