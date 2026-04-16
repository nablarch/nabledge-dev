# Nablarch 6u1 リリースノート

## No.1 システム日時をLocalDateTime型で取得できる機能を追加

**リリース区分**: 変更  **分類**: システム日時

SystemTimeUtilを用いたシステム日時の取得で、従来の Date 型に加え、Java 8から標準化されたDate and Time APIの LocalDateTime型での取得に対応しました。

参照先: https://nablarch.github.io/docs/6u1/publishedApi/nablarch-all/publishedApiDoc/programmer/nablarch/core/date/SystemTimeUtil.html

## No.2 ユニバーサルDAOのエンティティ生成機能をDate and Time APIに対応

**リリース区分**: 変更  **分類**: ユニバーサルDAO

ユニバーサルDAOで検索結果をマッピングするBeanに使用できるデータタイプとして、Java 8から標準化されたDate and Time APIの LocalDateTime型とLocalDate型に対応しました。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/libraries/database/universal_dao.html#id43

## No.3 BeanUtilをレコードに対応

**リリース区分**: 変更  **分類**: BeanUtil

BeanUtilで、Java 16より標準化されたレコードを使用できるよう機能追加しました。これにより、レコードオブジェクトの生成や、レコードオブジェクトからの値のコピーができるようになります。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/libraries/bean_util.html

## No.4 JSON形式のファイルを読み込む際、値の最後がエスケープ文字だとエラーが発生する問題に対応

**リリース区分**: 不具合  **分類**: 汎用データフォーマット

汎用データフォーマットでJSON形式のファイルを読み込む際、JSONの値の最後の文字がエスケープ文字(バックスラッシュ,Windows環境では円マーク:\)の場合、エラーが発生しJSONの解析に失敗する問題がありました。
例）input1:{ "key" : "value\\"}
　この場合、"value\"という文字列として解析するべきだが、解析に失敗していた。

今回の対応で、値の最後がエスケープ文字でもエラーなく解析できるようになりました。

また、Unicode形式でエスケープ文字を表す'\u005C'が含まれる場合、エスケープ処理を行わない文字列のバックスラッシュとして解析するべきです。しかし汎用データフォーマットではエスケープ処理の開始文字として読み取られ解析に失敗する不具合があったため対応しました。
例）input1:{ "key" : "\u005Cvalue"}
　この場合、"\value"という文字列として解析するべきだが、解析に失敗していた。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/libraries/data_io/data_format.html

## No.5 件数取得SQLをカスタマイズできるようにDialectインターフェースを拡張しました

**リリース区分**: 変更  **分類**: ユニバーサルDAO

ユニバーサルDAOでページング処理を行う場合、検索結果件数が必要となります。検索結果件数は、アプリケーションに設定された検索用のSQLを、Nablarchが件数取得SQLに加工し、検索実行前に発行しています。
検索用のSQLの処理が重く応答に時間がかかる場合、検索用のSQLと、検索用のSQLと同等の性能の件数取得SQLの2回SQLが発行されることで応答時間がより長くなる問題がありました。
通常、検索用のSQLに比べて件数取得時はソートが不要となるなど性能改善の可能性がありますが、件数取得SQLはNablarchが内部で自動生成しておりチューニングすることができませんでした。

この問題に対応するため、件数取得SQLをカスタマイズできるようにDialectインターフェースを拡張しました
これにより、性能劣化への対応等で件数取得SQLを変更したい場合に、自動生成されるSQLから任意のSQLに差し替えることができるようになります。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/libraries/database/database.html#database-dialect

## No.6 HTTPリクエストからリクエストパラメータを取得するAPIをアーキテクト向け公開APIに変更

**リリース区分**: 変更  **分類**: HTTPリクエスト

InjectFormを使わずActionクラスでバリデーションエラーをハンドリングする場合、HTTPリクエストから直接リクエストパラメータを取り出す必要があります。しかしHTTPリクエストからリクエストパラメータを取得する処理は、バリデーション前のパラメータを取得できてしまうため非公開APIとしています。
今回公開APIとして欲しいという要望を受け検討した結果、アーキテクトが基盤部品を作る場合に限定して公開することは有益と考えたため、HTTPリクエストからリクエストパラメータを取得するAPIをアーキテクト向け公開APIに変更しました。
InjectFormを使わずActionクラスでバリデーションエラーをハンドリングする場合は、このアーキテクト向け公開APIを使ってリクエストパラメータを取り出す時に必ずバリデーションが実行されるよう共通部品を作成してください。
アーキテクト向け公開APIのため、従来通りActionクラスで直接利用することは想定していません。
共通部品の作成例はNo.16のExampleを参考にしてください。

## No.7 RESTfulウェブサービス専用のHTTPリクエストクラスを追加

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

RESTfulウェブサービスでクエリパラメータ・パスパラメータを取得する場合、No.6同様非公開APIを使用する必要があります。
そのため、RESTfulウェブサービス向けにリクエストパラメータ取得処理を公開APIとした専用のHTTPリクエストを追加しました。
RESTfulウェブサービスにおいてはクエリパラメータ・パスパラメータの取得が頻繁に発生し得るためアーキテクト向けに限定せず、Actionなどから利用可能な公開APIとしています。必要に応じて取り出したパラメータをバリデーションするようにしてください。
なお、従来通り@Consumesアノテーションと@Validアノテーションを使ってパラメータをFormにバインドする場合はバインド時にバリデーションが実行されます。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/web_service/rest/feature_details/resource_signature.html

## No.8 分散トレーシングの依存ライブラリのバージョンを変更

**リリース区分**: 変更  **分類**: AWSにおける分散トレーシング

AWSにおける分散トレーシングの実装例として案内している依存ライブラリ（AWS X-Ray SDK、Jersey）がJakarta EE未対応のバージョンだったため、Jakarta EE対応済のバージョンに修正し、あわせてコード例の修正を行いました。
修正前後のバージョンは以下の通りです。
AWS X-Ray SDK ：2.4.0 → 2.15.0
Jersey：2.32 → 3.1.1

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/cloud_native/distributed_tracing/aws_distributed_tracing.html

## No.9 ブランクプロジェクトを Java 21 で動かす際に必要になる修正手順を追加

**リリース区分**: 変更  **分類**: ブランクプロジェクト

ブランクプロジェクトを Java 21 で動かす際に必要になる修正手順を、解説書に追加しました。
具体的な手順は、参照先に記載しているURLをご確認ください。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/blank_project/setup_blankProject/setup_Java21.html

## No.10 アプリケーションフレームワークのテスト環境を更新

**リリース区分**: 変更  **分類**: 稼働環境

テスト環境を以下の通り更新しました。赤字部分が変更箇所になります。
Java
　・Java SE 17/21
データベース
　・Oracle Database 12c/19c/21c/23c
　・IBM Db2 10.5/11.5
　・SQL Server 2017/2019/2022
　・PostgreSQL 10.0/11.5/12.2/13.2/14.0/15.2/16.2
アプリケーションサーバ
　・WildFly 31.0.1.Final
　・Apache Tomcat 10.1.17
　・Jakarta EE
　・Hibernate Validator 8.0.0.Final
　・JBeret 2.1.1.Final
MOM（メッセージ指向ミドルウェア）
　・IBM MQ 9.3

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/nablarch/platform.html#id3

## No.11 Java 21 に対応

**リリース区分**: 変更  **分類**: 全ブランクプロジェクト

Java 21 でもビルド・実行できるように、使用しているライブラリやMavenプラグインのバージョンを更新しました。
なお、Java 21で動かす際には、参照先の「Java21で使用する場合のセットアップ方法」を実施する必要があります。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/application_framework/blank_project/index.html

## No.12 SLF4Jのバージョンを2.0.11に変更

**リリース区分**: 変更  **分類**: SLF4Jアダプタ

SLF4Jは2.0からロギング実装を検索する仕組みが変更されており、SLF4Jアダプタはこの仕組みに対応していないため、SLF4J 2.0以降のバージョンではログ出力ができませんでした。
SLF4Jの2.0以降でもSL4Jアダプタが使用できるように、依存するSLF4Jのバージョンを更新（1.7.25 → 2.0.11）し、検索が適切に行われるよう対応しました。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/adaptors/slf4j_adaptor.html

## No.13 SLF4Jのバージョンを2.0.11に変更

**リリース区分**: 変更  **分類**: logアダプタ

SLF4Jが2.0以降でもlogアダプタが使用できるように、依存するSLF4Jのバージョンを更新しました。（1.7.22 → 2.0.11）

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/adaptors/log_adaptor.html

## No.14 Lettuceのバージョンを6.2.3.RELEASEに変更

**リリース区分**: 変更  **分類**: Redisストア(Lettuce)アダプタ

Redisストア(Lettuce)アダプタが依存するLettuceから推移的に依存するライブラリ（Netty）のバージョンとNablarchテスティングフレームワークが依存するバージョンが異なることに起因して、Redisストア(Lettuce)アダプタを使ったアプリケーションのリクエスト単体テスト実行時にエラーが発生していました。そのためLettuceのバージョンを更新（5.3.0.RELEASE → 6.2.3.RELEASE）しテストが実行できるように対応しました。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.html

## No.15 使用するIBM MQのバージョンを変更

**リリース区分**: 変更  **分類**: IBM MQアダプタ

IBM MQアダプタではWebSphere MQ 7.5付属のライブラリを使用していました。しかし現在は入手できない状況であるため、IBM MQ 9.3 を使用するように変更しました。
またバージョンアップに伴い、製品名がIBM WebSphere MQからIBM MQに変更されたため、解説書上のアダプタ名の記載を変更しました。

参照先: https://nablarch.github.io/docs/6u1/doc/application_framework/adaptors/webspheremq_adaptor.html

## No.16 HTTPリクエストからリクエストパラメータを取得する共通部品を追加

**リリース区分**: 変更  **分類**: HTTPリクエスト

No.6の使用例として、HTTPリクエストからリクエストパラメータを取得するユーティリティの実装例を追加しました。

## No.17 HTTPリクエストからリクエストパラメータを取得する処理を追加

**リリース区分**: 変更  **分類**: HTTPリクエスト

自動テスト内でHTTPリクエストの状態を検証したい場合など、No.6同様非公開APIを使用する必要があります。
そのため、テスティングフレームワーク向けにHTTPリクエストからリクエストパラメータを取得する公開APIを追加しました。
HTTPリクエストからリクエストパラメータを取得する場合は、HTTPリクエストのAPIではなく追加したAPIを使用するようにしてください。
なお、当該APIでは検証を目的としてリクエストパラメータを取り出すためバリデーションは実行しません。

参照先: https://nablarch.github.io/docs/6u1/publishedApi/nablarch-testing/publishedApiDoc/programmer/nablarch/test/core/http/HttpRequestTestSupport.html#getParamMap-nablarch.fw.web.HttpRequest-
