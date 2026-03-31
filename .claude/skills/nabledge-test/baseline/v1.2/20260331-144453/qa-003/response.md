**結論**: バッチのリクエスト単体テストで起動パラメータ（`requestPath`、`diConfig`、`userId`）を指定するには、テストデータのExcelファイルに `LIST_MAP=testShots` シートを作成し、各カラムに値を記述します。

**根拠**:

バッチリクエスト単体テストでは、`BatchRequestTestSupport` を継承したテストクラスを作成し、`execute()` メソッドを呼び出すことでテストを実行します。起動パラメータはJavaコードではなく、Excelのテストデータシートに記述します。

**テストクラスの作成**:
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

**Excelテストデータシート（`testSuccess`シート）の `LIST_MAP=testShots`**:

| no | description | expectedStatusCode | setUpTable | setUpFile | expectedTable | expectedFile | requestPath |
|---|---|---|---|---|---|---|---|
| 1 | ファイル入力 | 100 | default | default | default | | fileInputBatch |
| 2 | ユーザ削除 | 100 | default | | default | | userDeleteBatch |
| 3 | ファイル出力 | 100 | default | | fileInputBatch | default | fileOutputBatch |

`requestPath` カラムに指定する値は、本番起動時のコマンドライン引数 `-requestPath` と同じ値です。

**本番起動コマンドとテストの対応**:

```sh
java -classpath %CLASSPATH% nablarch.fw.launcher.Main \
  -diConfig %diConfig% \
  -requestPath %requestPath% \
  -userId %userId% %batchArgs%
```

| 本番引数 | 説明 | テストでの指定方法 |
|---|---|---|
| `-requestPath` | リクエストパス。書式: `(業務アクションクラス名)/(リクエストID)` | testShotsシートの `requestPath` カラム |
| `-diConfig` | コンポーネント設定ファイルへのパス | testShotsシートの `diConfig` カラム（常駐プロセス向け） |
| `-userId` | ユーザID | testShotsシートの `userId` カラム（常駐プロセス向け） |

**requestPath の書式例**:
```
ss11AC.B11AC011Action/RB11AC0110
```
通常 `"ss" + (機能ID) + "." + (アクションクラス名) + "/" + (リクエストID)` の形式です。リクエストIDは同一業務アクションクラスを実行するプロセスを複数起動する場合の識別子として用いられます。

**注意点**:
- 起動パラメータ（`requestPath` など）はJavaコード内ではなく、Excelのテストデータシートに記述します
- 必須パラメータ（`-diConfig`、`-requestPath`、`-userId`）のいずれかが指定されていない場合、バッチプロセスは異常終了します（終了コード127）
- `diConfig`・`requestPath`・`userId` カラムは、常駐プロセス（メッセージ送受信を行うプロセス）向けに必須となります

参照: `guide/nablarch-batch/nablarch-batch-02_basic.json#s5`, `processing-pattern/nablarch-batch/nablarch-batch-5.json#s1`, `processing-pattern/nablarch-batch/nablarch-batch-batch_single_shot.json#s1`, `development-tools/testing-framework/testing-framework-batch.json#s2`