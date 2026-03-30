**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、ExcelテストデータシートのtestShotsシート（`LIST_MAP=testShots`）に `requestPath` カラムを設け、実行したいバッチのリクエストパスを記述します。

**根拠**:

バッチのリクエスト単体テストは、`BatchRequestTestSupport` を継承したテストクラスと、Excelファイルのテストデータシートの組み合わせで実施します。

テストデータシート（`LIST_MAP=testShots`）に以下のカラムを定義し、`requestPath` カラムに起動パラメータ（リクエストパス）を指定します。

この `requestPath` の値は、コマンドラインからバッチを直接起動する際の `-requestPath` 引数と対応しています。

```sh
java -classpath %CLASSPATH% nablarch.fw.launcher.Main \
  -diConfig %diConfig% \
  -requestPath %requestPath% \
  -userId %userId% \
  %batchArgs%
```

テストクラスは以下のように `BatchRequestTestSupport` を継承して作成します。

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

**注意点**:
- `requestPath` はテストデータシートの `testShots` の各行に記述し、1行が1回のバッチ実行に対応します。
- バッチ取引単体テスト（リクエスト単体テスト）では、1シート内に複数のバッチ実行を記述することで、取引単位のテストが実施できます。

参照: `testing-framework-batch.json#s2`, `nablarch-batch-5.json#s1`, `testing-framework-RequestUnitTest_batch.json#s1`
