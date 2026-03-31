**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストケース一覧（`testShots`）のカラムに `diConfig`・`requestPath`・`userId`（必須3項目）を指定するか、`args[n]` 形式でコマンドライン引数を追加します。

---

**根拠**:

#### テストクラスの準備

バッチのリクエスト単体テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承して作成します。クラス名は `{Actionクラス名}RequestTest` とします。

#### テストケース一覧（testShots）での起動パラメータ指定

テストデータExcelの `testShots`（LIST_MAPデータタイプ）に以下の必須カラムを追加してバッチ起動パラメータを指定します：

| カラム名 | 説明 | 必須 |
|---|---|---|
| `diConfig` | コンポーネント設定ファイルパス（例: `classpath:batch-boot.xml`） | ○ |
| `requestPath` | 実行するアクションのクラス名/リクエストID（例: `SampleBatch`） | ○ |
| `userId` | バッチ実行ユーザID（例: `batch_user`） | ○ |

これらは `nablarch.fw.launcher.Main` の起動オプションに対応しており、いずれか欠けると異常終了します（終了コード = 127）。

```bash
# 実際のバッチ起動コマンドのイメージ
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

#### 追加の起動引数（args[n]）の指定

バッチ固有の追加コマンドライン引数は `args[n]`（nは0以上の整数）形式でカラムを追加して指定します。

> **重要**: 添字nは連続した整数でなければなりません（例: `args[0]`, `args[1]`, `args[2]`）。

また、`testShots` の標準カラム以外のカラムはコマンドラインオプションとして扱われます。例えばカラム名 `paramA` に値 `valueA` を設定すると `-paramA=valueA` として起動時に渡されます。

---

**注意点**:
- `diConfig`・`requestPath`・`userId` の3カラムはすべて必須です。1つでも欠けるとバッチが即時異常終了します。
- `args[n]` の添字は必ず連続した整数にしてください（飛び番は不可）。
- テストデータExcelファイルはテストソースコードと同じディレクトリに同名（拡張子のみ異なる）で格納します。

参照: `testing-framework-batch-02_RequestUnitTest.json#s3`, `testing-framework-batch-02_RequestUnitTest.json#s4`, `testing-framework-batch-02_RequestUnitTest.json#s1`, `handlers-main.json#s3`
