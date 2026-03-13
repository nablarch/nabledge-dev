**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストケース一覧（`testShots`）の各テストケース行に `args[n]`（nは0以上の整数）形式のカラムを追加して指定します。コマンドラインオプション形式のパラメータは `args[n]` 以外のカラム名で追加します。

---

**根拠**:

**バッチ起動引数（`args[n]`）の指定方法**

テストケース一覧（LIST_MAPデータタイプ、ID = `testShots`）の各テストケース行に、`args[n]`（nは0以上の整数）形式のカラムを追加します。

例：
| no | description | requestPath | userId | diConfig | args[0] | args[1] |
|----|-------------|-------------|--------|----------|---------|---------|
| 1  | 正常系テスト | /BATCH01    | batch  | batch.xml | file1.csv | OUT_DIR |

> **重要**: 添字nは連続した整数でなければなりません（0, 1, 2, …の順）。

**コマンドラインオプションの指定方法**

`args[n]` 以外のカラムを追加すると、コマンドラインオプションとみなされます。例えばカラム `paramA`（値 `valueA`）、`paramB`（値 `valueB`）を追加すると `-paramA=valueA -paramB=valueB` のオプションを指定したことになります。

**testShotsの必須カラム（参考）**

バッチリクエスト単体テストのテストケース一覧では以下のカラムが必須です：

| カラム名 | 説明 |
|---------|------|
| no | テストケース番号（1からの連番） |
| description | テストケースの説明 |
| expectedStatusCode | 期待するステータスコード |
| diConfig | バッチ実行時のコンポーネント設定ファイルパス |
| requestPath | バッチ実行時のリクエストパス |
| userId | バッチ実行ユーザID |

**テストクラスの作成**

テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承して作成し、以下のようにテストメソッドを定義します：

```java
@Test
public void testResigster() {
    execute();   // テストメソッド名をシート名として使用
}
```

---

**注意点**:
- `args[n]` の添字は連続した整数でなければなりません。不連続な場合は正しく引数が渡されません。
- コマンドラインオプション（`-key=value` 形式）と位置引数（`args[n]`）は別々の仕組みで指定します。混在させる場合は両方のカラムを追加します。

参照: `testing-framework-batch-02_RequestUnitTest.json#s4`, `testing-framework-batch-02_RequestUnitTest.json#s3`, `testing-framework-RequestUnitTest_batch.json#s1`
