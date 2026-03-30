**結論**: バッチのリクエスト単体テストで起動パラメータを指定するには、テストデータExcelファイルの `testShots` シートに `requestPath` 列を記載します。

`BatchRequestTestSupport` を継承したテストクラスを作成し、`execute()` を呼び出します。
testShots LIST_MAPの `requestPath` 列に起動パスを指定。コマンドライン起動時の `-requestPath` パラメータに相当。

参照: `development-tools/testing-framework/testing-framework-batch.json#s2`
