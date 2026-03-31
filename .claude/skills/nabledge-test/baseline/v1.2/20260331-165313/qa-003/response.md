**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストデータ（Excelファイル）の `testShots` シートの `requestPath` 列にリクエストパスを記述します。

**根拠**:

#### 1. テストクラスの作成

`BatchRequestTestSupport` を継承したテストクラスを作成します。

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

#### 2. testShots シートでの起動パラメータ指定

テストデータの `LIST_MAP=testShots` シートに `requestPath` 列を記述して起動時のリクエストパスを指定します。

**【testSuccessシート】** `LIST_MAP=testShots`

| no | description | expectedStatusCode | setUpTable | setUpFile | expectedTable | expectedFile | requestPath |
|---|---|---|---|---|---|---|---|
| 1 | ファイル入力 | 100 | default | default | default | | fileInputBatch |
| 2 | ユーザ削除 | 100 | default | | default | | userDeleteBatch |
| 3 | ファイル出力 | 100 | default | | fileInputBatch | default | fileOutputBatch |

#### 3. requestPath の書式

`requestPath` には以下の書式でリクエストパスを指定します。

```
(業務アクションクラス名)/(リクエストID)
```

実際のコマンドライン起動時の `-requestPath` オプションに対応します。

```bash
java ... nablarch.fw.launcher.Main -diConfig=file:./config/batch-config.xml \
                                   -requestPath=ss11AC.B11AC011Action/RB11AC0110 \
                                   -userId=batch_user
```

コマンドライン引数の種別:

| 種別 | 説明 | 取得方法 |
|---|---|---|
| オプション | `-キー名=値` 形式のkey-valueペア | `CommandLine#getParamMap()` |
| 引数 | オプション以外の単一値 | `CommandLine#getArgs()` |

主なコマンドラインオプション:

| キー名 | 説明 |
|---|---|
| `diConfig` | コンポーネント設定ファイルへのパス |
| `requestPath` | リクエストを特定するためのパス |
| `userId` | バッチ実行ユーザID |

**注意点**:
- `requestPath` 列は必須です（`testing-framework-batch.json` の testShots 定義より）
- テストクラスは `BatchRequestTestSupport` を継承する必要があります
- テストケース分割方針：基本は1シートにつき1テストケース。複数シートに分割する場合は `execute("シート名")` でシートを個別指定します

参照: `development-tools/testing-framework/testing-framework-batch.json#s2`, `guide/nablarch-batch/nablarch-batch-02_basic.json#s5`, `development-tools/testing-framework/testing-framework-batch.json#s1`, `processing-pattern/nablarch-batch/nablarch-batch-batch_single_shot.json#s1`

###