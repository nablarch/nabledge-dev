**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストケース一覧（`testShots`）のExcelデータに `args[n]`（nは0以上の整数）形式のカラムを追加して値を設定する。

**根拠**:

バッチ起動引数の指定方法は2種類ある。

**① 位置引数（`args[n]`形式）**

テストケース一覧に `args[0]`、`args[1]` のようなカラムを追加し、値を設定する。

```
| no | description | diConfig | requestPath | userId | args[0]       | args[1]   |
|----|-------------|----------|-------------|--------|---------------|-----------|
|  1 | 正常ケース   | batch.xml | BATCH001    | user01 | inputFile.csv | 20240101  |
```

**② コマンドラインオプション形式**

`args[n]` 以外の任意のカラム名を追加すると、コマンドラインオプションとして指定される。例えば `paramA`（値 `valueA`）、`paramB`（値 `valueB`）というカラムを追加すると、`-paramA=valueA -paramB=valueB` と指定したことになる。

```
| no | description | diConfig | requestPath | userId | paramA  | paramB  |
|----|-------------|----------|-------------|--------|---------|---------|
|  1 | 正常ケース   | batch.xml | BATCH001   | user01 | valueA  | valueB  |
```

テストクラスは `nablarch.test.core.batch.BatchRequestTestSupport` を継承して作成する。

```java
package nablarch.sample.ss21AC01;

import nablarch.test.core.batch.BatchRequestTestSupport;

public class B21AC01RequestTest extends BatchRequestTestSupport {
    // ...
}
```

**注意点**:
- `args[n]` の添字 n は連続した整数でなければならない（例: `args[0]`, `args[1]`, `args[2]`。途中を飛ばすと不可）。
- テストケース一覧（LIST_MAP、ID=`testShots`）では `diConfig`（コンポーネント設定ファイルパス）、`requestPath`（バッチリクエストパス）、`userId` は必須項目。

参照: `testing-framework-batch-02_RequestUnitTest.json#s4`, `testing-framework-batch-02_RequestUnitTest.json#s3`, `testing-framework-batch-02_RequestUnitTest.json#s1`