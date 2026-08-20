参照セクションのコンテンツが取得できなかったため、Nablarchの一般的な知識に基づいて回答します。

---

## Nablarchバッチアプリケーションの起動方法と `-requestPath` の書き方

### 起動コマンドの基本形

Nablarchバッチ（都度起動バッチ）は、以下のように `java` コマンドで起動します。

```bash
java -cp <クラスパス> nablarch.fw.launcher.Main \
  -diConfig <DIコンフィグファイル> \
  -requestPath <アクションクラス>/<リクエストID> \
  -userId <ユーザーID>
```

### `-requestPath` の書き方

```
-requestPath=<アクションクラスのFQCN>/<リクエストID>
```

| 部分 | 内容 |
|------|------|
| アクションクラスのFQCN | 実行するアクションクラスの完全修飾クラス名 |
| リクエストID | そのバッチを識別するID（任意の文字列） |

**例:**

```bash
-requestPath=com.example.batch.SampleBatchAction/SAMPLE_BATCH_001
```

または（クラス名のみの場合）:

```bash
-requestPath=SampleBatchAction/SAMPLE_BATCH_001
```

### 具体的な起動コマンド例

```bash
java -cp "target/classes:target/dependency/*" \
  nablarch.fw.launcher.Main \
  -diConfig classpath:batch-boot.xml \
  -requestPath com.example.batch.SampleBatchAction/SAMPLE_BATCH \
  -userId batch_user
```

### Mavenプロジェクトでの起動（ブランクプロジェクト標準）

```bash
mvn exec:java \
  -Dexec.mainClass=nablarch.fw.launcher.Main \
  -Dexec.args="-diConfig classpath:batch-boot.xml -requestPath com.example.SampleBatchAction/SAMPLE -userId batch"
```

### アクションクラスの実装イメージ

```java
public class SampleBatchAction extends BatchAction<SqlRow> {
    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // バッチ処理本体
        return new Result.Success();
    }
}
```

---

> **注意**: 参照ナレッジセクション（`nablarch-batch-architecture.json` 等）のコンテンツが取得できなかったため、上記はNablarchの一般知識に基づく回答です。プロジェクトの実際の設定と照合してご確認ください。