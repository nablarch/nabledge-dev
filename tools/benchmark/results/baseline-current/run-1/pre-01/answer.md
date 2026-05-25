**結論**: NablarchバッチアプリケーションはJavaの`nablarch.fw.launcher.Main`クラスをエントリーポイントとして起動し、コマンドライン引数`-requestPath`で実行するアクションクラスとリクエストIDを指定します。

**根拠**:

**起動コマンドの基本形**

```bash
java nablarch.fw.launcher.Main \
  -requestPath=アクションのクラス名/リクエストID \
  -diConfig classpath:xxx.xml \
  -userId ユーザID
```

Mavenから実行する場合は以下のように実行します。

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
  -Dexec.args="'-requestPath' 'ImportZipCodeFileAction/ImportZipCodeFile' '-diConfig' 'classpath:import-zip-code-file.xml' '-userId' '105'"
```

**`-requestPath`の書き方**

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例（完全修飾クラス名）
-requestPath=com.sample.SampleBatchAction/BATCH0001

# 指定例（クラス名のみ）
-requestPath=ImportZipCodeFileAction/ImportZipCodeFile
```

| 要素 | 説明 |
|------|------|
| アクションのクラス名 | 実行するアクションクラス（完全修飾名またはクラス名のみ） |
| リクエストID | バッチプロセスの識別子。同一アクションを複数プロセス起動する場合の識別に使用 |

**処理の流れ**

1. 共通起動ランチャ（`Main`）がハンドラキューを実行
2. データリーダが入力データを1件ずつ読み込む
3. ディスパッチハンドラが`-requestPath`で指定されたリクエストパスをもとにアクションクラスを特定してキューに追加
4. アクションクラスがデータレコード1件ごとに業務ロジックを実行
5. 全データ処理完了後、プロセス終了コードが返される

**注意点**:
- `Main`クラスはスタンドアロンのアプリケーションとして起動するため、javaコマンドから直接呼び出す
- リクエストIDは各バッチプロセスの識別子として機能する。同一アクションを複数プロセスで起動する場合はリクエストIDを変えることで区別できる
- 常駐バッチも同じ起動形式を使用するが、新規開発ではテーブルをキューとして使ったメッセージング方式の利用を推奨（マルチスレッド時の処理遅延問題を回避するため）

参照: `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s1`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s3`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s1`