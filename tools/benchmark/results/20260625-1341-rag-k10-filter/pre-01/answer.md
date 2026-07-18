Nablarchバッチアプリケーション（都度起動バッチ）の起動方法と `-requestPath` の書き方は以下の通りです。

#### 起動コマンド

```bash
java -jar <jarファイル> \
  -requestPath=<アクションクラス名>/<リクエストID> \
  -diConfig=<DIコンフィグファイルパス> \
  -userId=<ユーザーID>
```

#### `-requestPath` の書き方

```
-requestPath=<完全修飾アクションクラス名>/<リクエストID>
```

**例:**

```bash
-requestPath=com.example.action.SampleBatchAction/SAMPLE_BATCH001
```

| 要素 | 説明 | 例 |
|------|------|----|
| アクションクラス名 | `BatchAction` を実装したクラスの完全修飾名 | `com.example.action.SampleBatchAction` |
| リクエストID | スラッシュ区切りで指定する任意のID | `SAMPLE_BATCH001` |

#### 起動例（全体）

```bash
java -jar app.jar \
  -requestPath=com.example.action.SampleBatchAction/SAMPLE_BATCH001 \
  -diConfig=classpath:batch-boot.xml \
  -userId=batchUser
```

#### ポイント

- **`-requestPath`** は `アクションクラス/リクエストID` の形式で指定します。スラッシュ（`/`）で区切ります。
- **`-diConfig`** にはハンドラキューを定義したコンポーネント設定ファイルを指定します（`classpath:` プレフィックスでクラスパス指定可）。
- **`-userId`** は実行ユーザーIDとして使用されます。

> **注意:** 参照セクション（`nablarch-batch-architecture.json` 等）のコンテンツが今回取得できなかったため、上記はNablarch公式ドキュメントの一般知識に基づく回答です。正確な情報はNablarch公式ドキュメントの「バッチアプリケーション」章をご確認ください。