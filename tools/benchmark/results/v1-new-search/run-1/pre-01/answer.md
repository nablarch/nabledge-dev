**結論**: `java nablarch.fw.launcher.Main` コマンドに3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`）を指定して起動します。`-requestPath` は `アクションのクラス名/リクエストID` の形式で指定します。

**根拠**:

起動の書式は以下の通りです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**3つの必須オプション**

| オプション | 内容 |
|-----------|------|
| `-diConfig` | システムリポジトリの設定ファイルのパスを指定する |
| `-requestPath` | 実行するアクションとリクエストIDを指定する |
| `-userId` | ユーザIDを指定する（セッションコンテキスト変数 `user.id` に格納される） |

いずれかが欠けていた場合、即座に異常終了します（終了コード = 127）。

**`-requestPath` の書式**

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 例：パッケージ付きのフルクラス名
-requestPath=com.sample.SampleBatchAction/BATCH0001

# 例：クラス名のみ（パッケージ省略）
-requestPath=ImportZipCodeFileAction/ImportZipCodeFile
```

リクエストIDは各バッチプロセスの識別子として使われます。同一のアクションクラスを複数プロセスで起動する場合に、このリクエストIDが識別子となります。

**Maven経由での起動例**（ブランクプロジェクトの場合）

```bash
# 都度起動バッチ
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"

# 常駐バッチ
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:resident-batch-boot.xml' '-requestPath' 'SampleResiBatch' '-userId' 'batch_user'"
```

**注意点**:
- `-requestPath` で指定するアクションクラス名には、パッケージを含む完全修飾名または相対パッケージ名を指定できます。`RequestPathJavaPackageMapping` ハンドラで `basePackage` を設定している場合は、そのパッケージからの相対パスで指定します。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3, blank-project-setup-NablarchBatch.json:s9, nablarch-batch-getting-started-nablarch-batch.json:s1