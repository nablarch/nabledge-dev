**結論**: Nablarchのバッチには「Nablarchバッチアプリケーション」と「Jakarta Batchに準拠したバッチアプリケーション」の2種類があり、それぞれ起動方法が異なります。

---

**根拠**:

### 1. Nablarchバッチアプリケーションの起動方法

`nablarch.fw.launcher.Main` クラスをjavaコマンドで起動します。以下の3つのオプションは必須です（いずれかが欠けると即時異常終了、終了コード = 127）。

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパスを指定 |
| `-requestPath` | `実行するアクションのクラス名/リクエストID` の形式で指定 |
| `-userId` | ユーザID |

**起動コマンド例:**
```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**Mavenを使った起動例（開発時）:**
```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

**任意オプションパラメータの追加方法:**
```bash
java nablarch.fw.launcher.Main \
  -optionName optionValue
```
アプリケーション内では `ExecutionContext#getSessionScopedVar("optionName")` で値を取得できます。

---

### 2. Jakarta Batchに準拠したバッチアプリケーションの起動方法

`nablarch.fw.batch.ee.Main` クラスを使用します。実行引数には対象JOBのXMLファイル名（`.xml` を除いたファイル名）を指定します。

**起動コマンド例:**
```bash
java nablarch.fw.batch.ee.Main jobName
```

**ジョブパラメータを指定する場合:**

起動オプションは名前に `--` を付加し、名前の次の引数に値を設定します。

```bash
# 「option1=value1」と「option2=value2」の2つのjobParametersが設定される
$ java nablarch.fw.batch.ee.Main jobName --option1 value1 --option2 value2
```

---

### 3. 設定ファイルの使い分け（Nablarchバッチ）

バッチの種類によって起動時に指定する設定ファイルが異なります。

| 設定ファイル | 用途 |
|---|---|
| `batch-boot.xml` | 都度起動バッチ起動時に指定する設定ファイル |
| `mail-sender-boot.xml` | メール送信バッチ起動時に指定する設定ファイル |
| `resident-batch-boot.xml` | テーブルをキューとして使ったメッセージング起動時に指定する設定ファイル |

---

**注意点**:
- Nablarchバッチアプリケーションで `-diConfig`、`-requestPath`、`-userId` のいずれかのオプションが欠けると即時異常終了（終了コード = 127）します
- Jakarta Batchに準拠したバッチアプリケーションで起動オプションを指定する場合は、`--` プレフィックスを使用し、指定した値は `JobOperator#start` の `jobParameters` に設定されます
- コンテナ用バッチプロジェクト（`myapp-container-batch`）の場合、コンテナイメージの実行手順は通常のコンテナ用Nablarchバッチプロジェクトと同じです

参照: `handlers-main.json#run-application`, `jakarta-batch-run_batch_application.json#run-batch-application`, `blank-project-setup_NablarchBatch.json#connectivity-check-batch`, `handlers-main.json#option-parameter`
