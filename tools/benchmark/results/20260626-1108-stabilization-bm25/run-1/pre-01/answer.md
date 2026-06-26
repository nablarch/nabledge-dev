## Nablarchバッチアプリケーションの起動方法と -requestPath の書き方

**結論**: Nablarchバッチアプリケーションは `java nablarch.fw.launcher.Main` コマンドで起動し、`-requestPath` オプションに「アクションのクラス名/リクエストID」を指定する。

---

**根拠**:

**起動コマンドの例**

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**必須オプション（3つ全て必須。1つでも欠けると終了コード 127 で異常終了）**

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

**-requestPath の書式**

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われる。同一のアクションクラスを複数プロセスで起動する場合の識別にも用いる。

**RequestPathJavaPackageMappingを使った短縮指定（任意）**

`RequestPathJavaPackageMapping` ハンドラを設定すると、クラス名の完全修飾名ではなくベースパッケージからの相対パスで指定できる。

```xml
<component class="nablarch.fw.handler.RequestPathJavaPackageMapping">
  <property name="basePath"    value="/app/action/" />
  <property name="basePackage" value="nablarch.application" />
</component>
```

上記設定の場合、`nablarch.application.xxx.ExampleBatchAction` クラスへのディスパッチは次のように指定できる：

```
-requestPath=/app/action/xxx/ExampleBatchAction
```

---

**注意点**:

- `-diConfig`、`-requestPath`、`-userId` は省略不可。いずれかが欠けると即座に異常終了（終了コード 127）する。
- リクエストIDは必ず指定すること（`クラス名/リクエストID` の `/リクエストID` 部分は必須）。

---

参照: nablarch-batch-architecture.json:s1, nablarch-batch-architecture.json:s2, handlers-main.json:s3, handlers-request-path-java-package-mapping.json:s4, handlers-request-path-java-package-mapping.json:s5