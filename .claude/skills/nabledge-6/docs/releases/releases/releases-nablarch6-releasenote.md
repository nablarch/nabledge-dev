# 

## 

■Nablarch 6 リリースノート
5u23からの変更点を記載しています。
コンテンツ  No.  分類  リリース
区分  タイトル  概要  修正後のバージョン
（※1）  不具合の起因バージョン
（※2）  システムへの
影響の可能性
（※3）  システムへの影響の可能性の内容と対処  参照先  JIRA issue
(※4)
モジュール  Nablarch
アプリケーションフレームワーク
オブジェクトコード、ソースコード  1  全般  変更  Jakarta EE 10対応  Jakarta EE 10に対応しました。
これにより、Jakarta EE 10に対応しているアプリケーションサーバ上で動作するようになりました。

Nablarch 6 のソースコードは、現時点では v6-master ブランチにて公開します。  ※モジュールバージョン一覧を参照  -  -  あり  Jakarta EE 10 に対応したアプリケーションサーバで動作させる必要があります。
また、Jakarta EE 10への移行に伴い、パッケージ名や依存関係などを変更する必要があります。変更内容の詳細については、解説書のマイグレーションガイドをご参照ください。  https://nablarch.github.io/docs/6/doc/migration/index.html  NAB-411
2  稼働環境  変更  必要Javaバージョンの変更  No.1 の対応に伴い、動作に必要なJavaのバージョンを 17 に変更しました。  -  -  -  あり  実行環境のJavaバージョンを17にする必要があります。  -  NAB-411
アダプタ
オブジェクトコード、ソースコード  3  全般  変更  Nablarch 6 対応（動作検証中）  Nablarch 6 に対応するため依存関係を変更しました。

動作については現在検証中であるため、動作が保証されていない状態であることにご注意ください。次期バージョンの 6u1 では動作を保証した状態となる予定です。  ※モジュールバージョン一覧を参照  -  -  なし  -  -  NAB-411
Example
オブジェクトコード、ソースコード  4  全般  追加  Nablarch 6 対応  Nablarch 6 に対応したサンプルを追加しました。

Nablarch 6 に対応したサンプルは、現時点では v6-master ブランチにて公開します。  ※モジュールバージョン一覧を参照  -  -  なし  -  -  NAB-411
ETL基盤
解説書  5  削除  解説書からの削除  ETL基盤はNablarch 6 に対応しないため、解説書から削除しました。  -  -  -  なし  -  -  NAB-411
帳票ライブラリ
解説書  6  削除  解説書からの削除  帳票ライブラリはNablarch 6 に対応しないため、解説書から削除しました。  -  -  -  なし  -  -  NAB-411
ワークフローライブラリ
解説書  7  削除  解説書からの削除  ワークフローライブラリはNablarch 6 に対応しないため、解説書から削除しました。  -  -  -  なし  -  -  NAB-411
テスティングフレームワーク
オブジェクトコード、ソースコード  8  全般  変更  Nablarch 6 対応  Nablarch 6 で開発したアプリケーションのテストに対応しました。  ※モジュールバージョン一覧を参照  -  -  なし  -  -  NAB-411
Nablarch実装例集
解説書  9  実装例集  変更  実装例集の一時削除  実装例集で案内しているサンプルは Nablarch 6 に未対応のため、解説書から一時的に削除しました。
次バージョンの6u1にて改めて公開予定です。  -  -  -  なし  -  -  NAB-411
■バージョンアップ手順
本リリースの適用手順は、解説書の「Nablarch 5から6への移行ガイド」をご参照ください。
https://nablarch.github.io/docs/6/doc/migration/index.html
■モジュールバージョン一覧
リリースするモジュールおよびバージョンは、次の通りです。（内部向けモジュールは除く）
種類  Group ID  Artifact ID  バージョン
ブランクプロジェクト  com.nablarch.archetype  nablarch-single-module-archetype  6
Example  com.nablarch.example  nablarch-example-web  6
Example  com.nablarch.example  nablarch-example-thymeleaf-web  6
Example  com.nablarch.example  nablarch-example-rest  6
Example  com.nablarch.example  nablarch-example-http-messaging-send  6
Example  com.nablarch.example  nablarch-example-http-messaging  6
Example  com.nablarch.example  nablarch-example-batch-ee  6
Example  com.nablarch.example  nablarch-example-batch  6
Example  com.nablarch.example  nablarch-example-mom-delayed-send  6
Example  com.nablarch.example  nablarch-example-mom-sync-send-batch  6
Example  com.nablarch.example  nablarch-example-mom-delayed-receive  6
Example  com.nablarch.example  nablarch-example-mom-sync-receive  6
Example  com.nablarch.example  nablarch-example-db-queue  6
Example  com.nablarch.example  nablarch-example-mom-testing-common  6
アプリケーションフレームワーク  com.nablarch.configuration  nablarch-main-default-configuration  2.0.0
アプリケーションフレームワーク  com.nablarch.configuration  nablarch-testing-default-configuration  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-backward-compatibility  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-auth  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-auth-jdbc  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-code  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-code-jdbc  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-dao  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-databind  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-date  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-encryption  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-exclusivecontrol  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-exclusivecontrol-jdbc  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-idgenerator  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-idgenerator-jdbc  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-common-jdbc  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-applog  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-beans  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-dataformat  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-jdbc  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-message  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-repository  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-transaction  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-validation  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-core-validation-ee  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-batch  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-batch-ee  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-jaxrs  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-messaging  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-messaging-http  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-messaging-mom  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-standalone  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-web  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-web-dbstore  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-web-doublesubmit-jdbc  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-web-extension  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-web-hotdeploy  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-fw-web-tag  2.0.0
アプリケーションフレームワーク  com.nablarch.framework  nablarch-mail-sender  2.0.0
テスティングフレームワーク  com.nablarch.framework  nablarch-testing  2.0.0
テスティングフレームワーク  com.nablarch.framework  nablarch-testing-jetty12  1.0.0
テスティングフレームワーク  com.nablarch.framework  nablarch-testing-rest  2.0.0
アダプタ  com.nablarch.integration  nablarch-jackson-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-jboss-logging-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-jersey-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-resteasy-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-router-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-slf4j-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-doma-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-jsr310-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-mail-sender-freemarker-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-mail-sender-thymeleaf-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-mail-sender-velocity-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-web-thymeleaf-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-lettuce-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-micrometer-adaptor  2.0.0
アダプタ  com.nablarch.integration  slf4j-nablarch-adaptor  2.0.0
アダプタ  com.nablarch.integration  nablarch-wmq-adaptor  2.0.0
開発ツール  com.nablarch.tool  nablarch-toolbox  2.0.0
