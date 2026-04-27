**結論**: バッチのリクエスト単体テストでは、テストデータを定義する Excel ファイル（データシート）の `testShots` （LIST_MAP データタイプ）に、起動パラメータ（コマンドライン引数に相当する値）を 1 テストケースごとに次の 3 カラムで指定します。

- `diConfig`: バッチを実行する際のコンポーネント設定ファイルへのパス（必須）
- `requestPath`: バッチを実行する際のリクエストパス（必須）
- `userId`: バッチ実行ユーザID（必須）

これら 3 項目はいずれもコマンドライン引数（`Main#execute` に渡すパラメータ）に対応しており、テストショットごとに個別に切り替えられます。

**根拠**: 知識ファイルには、バッチのリクエスト単体テストで使用するデータシート（`testShots`）の仕様として以下の記載があります（抜粋）。

| カラム名 | 説明 | 必須 |
|---|---|---|
| diConfig | バッチを実行する際のコンポーネント設定ファイルへのパスを記載する。（コマンドライン引数 を参照） | 必須 |
| requestPath | バッチを実行する際のリクエストパスを記載する。（コマンドライン引数 を参照） | 必須 |
| userId | バッチ実行ユーザIDを記載する。（コマンドライン引数 を参照） | 必須 |

テストクラスは `BatchRequestTestSupport` を継承し、このクラスが準備したテストデータ（上記 `testShots`）を元にリクエスト単体テストを実行します。`BatchRequestTestSupport` は「バッチリクエスト単体テストで必要となるテスト準備機能、各種アサートを提供する」コンポーネントで、`StandaloneTestSupportTemplate`（コンテナ外で動作する処理のテスト実行環境）や `MainForRequestTesting`（テスト用メインクラス。テスト実行時の差分を吸収する）と組み合わせて動作します。

**注意点**:
- `diConfig` / `requestPath` / `userId` はいずれも **必須** カラムです。省略できません。
- デフォルトのグループIDを使う場合は `default` と記載します（個別グループIDと併用可能）。
- ダウンロードファイルの期待値確認など詳細な記述方法は、「リクエスト単体テストの実施方法(バッチ)」ドキュメント側に委譲されています。

参照:
- development-tools/testing-framework/testing-framework-02-requestunittest-batch.json#s5
- development-tools/testing-framework/testing-framework-02-requestunittest-batch.json#s17
- development-tools/testing-framework/testing-framework-RequestUnitTest-batch.json#s3
- development-tools/testing-framework/testing-framework-RequestUnitTest-batch.json#s7
