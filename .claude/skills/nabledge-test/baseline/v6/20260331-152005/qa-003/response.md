**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストケース一覧（`testShots`）のカラムとして追加します。方法は2通りあります。

1. **`args[n]` 形式** — 位置引数（コマンドライン引数）を指定する場合
2. **任意カラム名** — コマンドラインオプション（`-key=value` 形式）を指定する場合

---

**根拠**:

### 必須の起動パラメータ（標準カラム）

テストケース一覧（`testShots`）には以下の3カラムが必須です。これらはバッチ起動時の `-diConfig`、`-requestPath`、`-userId` オプションに対応します。

| カラム名 | 必須 | 説明 |
|---|---|---|
| `diConfig` | ○ | バッチ実行時のコンポーネント設定ファイルパス |
| `requestPath` | ○ | バッチ実行時のリクエストパス（`実行Actionクラス名/リクエストID` 形式） |
| `userId` | ○ | バッチ実行ユーザID |

### 追加の起動パラメータを渡す方法

**`args[n]` 形式（位置引数）**:

バッチ起動時の位置引数は `args[n]`（n は 0 以上の整数）形式でカラムを追加します。

> **重要**: 添字 n は連続した整数でなければなりません（`args[0]`, `args[1]`, `args[2]`, ...）。

**任意カラム名（コマンドラインオプション）**:

標準カラム以外のカラムはコマンドラインオプションとして扱われます。例えば、カラム名 `paramA` に値 `valueA` を設定すると、`-paramA=valueA` として扱われます。

### バッチ実行時のコマンドとの対応

実際のバッチ起動コマンドは以下のとおりです:

```bash
java nablarch.fw.launcher.Main   -diConfig file:./batch-config.xml   -requestPath admin.DataUnloadBatchAction/BC0012   -userId testUser
```

テストケース一覧でこれらを指定することで、`BatchRequestTestSupport` がテスト実行時に同等の起動を行います。

---

**注意点**:
- `args[n]` を使用する場合、添字は連続した整数でなければなりません（`args[0]`, `args[2]` のように飛ばすことはできません）。
- `diConfig`、`requestPath`、`userId` の3カラムはいずれも必須です。欠けると即時異常終了します（終了コード = 127）。
- テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承して作成します。

参照: `testing-framework-batch-02_RequestUnitTest.json#s4`、`testing-framework-batch-02_RequestUnitTest.json#s3`、`handlers-main.json#s3`