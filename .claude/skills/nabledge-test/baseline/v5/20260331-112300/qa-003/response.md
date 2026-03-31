**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、Excelテストデータのテストケース一覧（`testShots`）に専用のカラムを追加する。

**根拠**:

**テストクラスの準備**

テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承し、クラス名は `{Actionクラス名}RequestTest` とする。

```java
@Test
public void testBatch() {
    execute();  // テストメソッド名をシート名として使用
}
```

**起動パラメータの指定方法**

テストケース一覧（LIST_MAP、ID = `testShots`）に以下のカラムで起動パラメータを指定する:

| カラム名 | 説明 | 必須 |
|---|---|---|
| `diConfig` | バッチ実行時のコンポーネント設定ファイルパス（例: `classpath:batch-boot.xml`） | ○ |
| `requestPath` | バッチ実行時のリクエストパス（例: `SampleBatch`） | ○ |
| `userId` | バッチ実行ユーザID（例: `batch_user`） | ○ |
| `args[n]` | コマンドライン引数（n は 0 以上の連続した整数） | |

**コマンドライン引数（`args[n]`）の追加方法**

バッチに渡すコマンドライン引数は `args[n]` 形式のカラムで指定する。

> **重要**: 添字 n は連続した整数でなければならない。

また、`args[n]` 以外のカラム名を追加するとコマンドラインオプションとして扱われる。例えばカラム `paramA`（値 `valueA`）、`paramB`（値 `valueB`）を追加すると `-paramA=valueA -paramB=valueB` のオプションを指定したことになる。

**注意点**:
- `diConfig`、`requestPath`、`userId` は必須カラムであり、省略できない
- `args[n]` の添字は連続した整数（0, 1, 2, ...）でなければならない。飛び番は不可
- `args[n]` 以外の任意カラムを追加すると自動的にコマンドラインオプション（`-key=value` 形式）として解釈される

参照: `testing-framework-batch-02_RequestUnitTest.json#s3`, `testing-framework-batch-02_RequestUnitTest.json#s4`, `testing-framework-batch-02_RequestUnitTest.json#s1`
