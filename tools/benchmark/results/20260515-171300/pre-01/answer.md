**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスをjavaコマンドで起動し、`-requestPath` 引数でアクションクラスとリクエストIDを指定します。

**根拠**:

## 起動方法

Nablarchバッチアプリケーションはスタンドアロンのアプリケーションとして、javaコマンドから直接起動します。エントリポイントは **共通起動ランチャ (`nablarch.fw.launcher.Main`)** です。

## `-requestPath` の書式

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- **アクションのクラス名**: 実行するアクションクラスの完全修飾クラス名
- **リクエストID**: 各バッチプロセスの識別子。同一アクションクラスを複数プロセスで起動する場合の識別に使われます

## 実行例（Mavenを使った起動）

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-requestPath' 'ImportZipCodeFileAction/ImportZipCodeFile' \
                 '-diConfig' 'classpath:import-zip-code-file.xml' \
                 '-userId' '105'"
```

よく合わせて指定する引数:
- `-diConfig`: DIコンテナの設定ファイル（XMLのクラスパス）
- `-userId`: 実行ユーザID

## 処理の流れ

1. 共通起動ランチャ(Main)がハンドラキューを実行
2. リクエストディスパッチハンドラが `-requestPath` をもとに呼び出すアクションクラスを特定し、ハンドラキューの末尾に追加
3. アクションクラスがデータレコード1件ごとの業務ロジックを実行

**注意点**:
- リクエストIDは省略できません。`アクションクラス名/リクエストID` の形式で両方を指定する必要があります
- `-diConfig` でコンポーネント定義XMLを指定しないと起動できません
- 常駐バッチを新規開発する場合は、テーブルをキューとして使ったメッセージングの利用が推奨されています（マルチスレッドでの処理遅延問題のため）

参照: `nablarch-batch-architecture.json#s1`, `nablarch-batch-architecture.json#s2`, `nablarch-batch-architecture.json#s3`, `nablarch-batch-getting-started-nablarch-batch.json#s1`