**結論**: NablarchバッチはJavaコマンドで `nablarch.fw.launcher.Main` クラスを指定して起動します。`-requestPath` には `アクションのクラス名/リクエストID` の書式で実行するアクションを指定します。

**根拠**:

起動コマンドの書式と必須オプション3つ（すべて必須、欠けると終了コード127で異常終了）:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

| オプション | 役割 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス（XMLファイル） |
| `-requestPath` | 実行するアクションとリクエストIDの指定 |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

**`-requestPath` の書式**:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- **アクションのクラス名**: 実行するバッチアクションクラスの完全修飾名（FQCN）またはベースパスからの相対パス
- **リクエストID**: 各バッチプロセスの識別子。同一アクションクラスを複数プロセスで起動する場合の区別に使用

**ディスパッチハンドラのベースパス設定による省略**:

ハンドラキューにリクエストディスパッチハンドラ（`RequestPathJavaPackageMapping`）を設定している場合、`basePackage` と `basePath` の設定によってクラス名を省略して記述できます。

```xml
<component class="nablarch.fw.handler.RequestPathJavaPackageMapping">
  <property name="basePath"    value="/app/action/" />
  <property name="basePackage" value="nablarch.application" />
</component>
```

上記設定の場合、`nablarch.application.ExampleBatchAction` クラスへのディスパッチは `-requestPath=/app/action/ExampleBatchAction` と指定します。

**処理の流れ**:

1. `Main` クラスがハンドラキューを実行
2. `DispatchHandler`（リクエストディスパッチハンドラ）が `-requestPath` で指定されたリクエストパスを元にアクションクラスを特定し、ハンドラキューの末尾に追加
3. アクションクラスがレコード1件ごとの業務ロジックを実行

**注意点**:
- `-diConfig`、`-requestPath`、`-userId` の3オプションはすべて必須。いずれかが欠けると即座に異常終了（終了コード = 127）

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3, nablarch-batch-architecture.json:s3, handlers-request-path-java-package-mapping.json:s4