**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、Excelテストデータファイルの `LIST_MAP=testShots` シートの `requestPath` 列に値を設定します。

```java
public class B21AC01Test extends BatchRequestTestSupport {
    @Test
    public void testSuccess() {
        execute();
    }
}
```

参照: `development-tools/testing-framework/testing-framework-batch.json#s2`
