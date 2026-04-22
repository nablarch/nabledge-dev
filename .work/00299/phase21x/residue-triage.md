# Residue Triage (v6 pilot)

## Aggregate

- match (exact): 12807
- match (space-normalised): 58
- miss: 3152
- coverage (match + space): 80.3%

## Top files by unmatched-line count (after pilot reduction)

| File | Source lines | Missing |
|---|---:|---:|
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/tag.rst | 780 | 169 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/tag/tag_reference.rst | 215 | 127 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/01_entityUnitTestWithBeanValidation.rst | 207 | 98 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/01_ClassUnitTest/01_entityUnitTest/02_entityUnitTestWithNablarchValidation.rst | 205 | 84 |
| .lw/nab-official/v6/nablarch-document/ja/biz_samples/03/index.rst | 279 | 81 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/01_Abstract.rst | 222 | 81 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/batch.rst | 244 | 77 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/log.rst | 376 | 74 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/system_messaging/mom_system_messaging.rst | 392 | 73 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/02_RequestUnitTest.rst | 213 | 70 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/database.rst | 392 | 67 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/index.rst | 220 | 57 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst | 400 | 53 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/data_io/data_bind.rst | 183 | 53 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst | 265 | 42 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/validation/nablarch_validation.rst | 189 | 38 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.rst | 230 | 38 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/02_DbAccessTest.rst | 193 | 37 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/repository.rst | 310 | 36 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/03_Tips.rst | 239 | 36 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/web/feature_details.rst | 83 | 35 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/common/request_handler_entry.rst | 55 | 35 |
| .lw/nab-official/v6/nablarch-document/ja/development_tools/testing_framework/guide/development_guide/06_TestFWGuide/RequestUnitTest_real.rst | 94 | 35 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/nablarch_batch/architecture.rst | 94 | 33 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/data_io/data_format.rst | 181 | 33 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/messaging/mom/architecture.rst | 93 | 32 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/mail.rst | 144 | 31 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/log/sql_log.rst | 203 | 29 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/handlers/web/SessionStoreHandler.rst | 73 | 28 |
| .lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/system_messaging/http_system_messaging.rst | 121 | 25 |

## Residue samples (up to 50)

- **.lw/nab-official/v6/nablarch-document/ja/migration/index.rst**
    - `プロジェクトによっては不要な手順が含まれる可能性があるが、その場合は適宜取捨選択して読み進めること（例えば、 waitt-to-jetty や update-ntf-jetty はウェブプロジェクト固有の手順なので、バッチプロジェクトでは読み飛ばして問題ない）。`
- **.lw/nab-official/v6/nablarch-document/ja/migration/index.rst**
    - `また、ここで記載されていない依存関係を変更するための参考として、本ページ末尾の付録に java_ee_jakarta_ee_comparation を記載する。`
- **.lw/nab-official/v6/nablarch-document/ja/migration/index.rst**
    - `詳細については micrometer_collaboration を参照のこと。`
- **.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst**
    - ``Nablarch APIドキュメント <nablarch-all/NablarchApi/>``
- **.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst**
    - ``Nablarch Testing APIドキュメント <nablarch-testing/NablarchTestingApi/>``
- **.lw/nab-official/v6/nablarch-document/ja/releases/index.rst**
    - ``全リリースノート一括ダウンロード <./nablarch-6-OSS-all-releasenote.zip>``
- **.lw/nab-official/v6/nablarch-document/ja/external_contents/index.rst**
    - `| Nablarchシステム開発ガイド(外部サイト) https://fintan.jp/page/252/`
- **.lw/nab-official/v6/nablarch-document/ja/external_contents/index.rst**
    - `| 開発標準(外部サイト) https://fintan.jp/page/1868/#development-standards`
- **.lw/nab-official/v6/nablarch-document/ja/about_nablarch/license.rst**
    - ``LICENSE.txt <./LICENSE.txt>``
- **.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst**
    - `| 6 ： プロダクトバージョン6 初期リリース`
- **.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst**
    - `| 6u1 ： プロダクトバージョン6 アップデートリリース１`
- **.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst**
    - `マイナーバージョンアップ時にインクリメントされます。 |br|`
- **.lw/nab-official/v6/nablarch-document/ja/examples/index.rst**
    - `setup_blank_project_for_Java21`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/web_thymeleaf_adaptor.rst**
    - `extdoc:`ThymeleafResponseWriter<nablarch.fw.web.handler.responsewriter.thymeleaf.ThymeleafResponseWriter>` を\`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/web_thymeleaf_adaptor.rst**
    - `extdoc:`HttpResponseHandler<nablarch.fw.web.handler.HttpResponseHandler>` へ設定する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/web_thymeleaf_adaptor.rst**
    - `extdoc:`ThymeleafResponseWriter<nablarch.fw.web.handler.responsewriter.thymeleaf.ThymeleafResponseWriter>` は\`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/jaxrs_adaptor.rst**
    - ``RESTfulウェブサービス <restful_web_service>` で使用するための以下のアダプタを提供する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/jaxrs_adaptor.rst**
    - `extdoc:`JaxRsMethodBinderFactory#handlerList <nablarch.fw.jaxrs.JaxRsMethodBinderFactory.setHandlerList(java.util.List)>``
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/jaxrs_adaptor.rst**
    - `body_convert_handler の設定(以下のコンバータが設定される)`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst**
    - `本アダプタでは、このレジストリを repository に登録するための ComponentFactory を提供している。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst**
    - `ここでは、 LoggingMeterRegistry(外部サイト、英語) をコンポーネントとして登録する LoggingMeterRegistryFactory を例にして設定方法について説明する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst**
    - `Micrometerには、 MeterBinder(外部サイト、英語) というインタフェースが存在する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/lettuce_adaptor.rst**
    - `health_check_endpoint_handler`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst**
    - ``NablarchのMOMメッセージング機能 <mom_messaging>` で IBM MQ(外部サイト、英語) https://www.ibm.com/docs/en/ibm-mq/9.3?topic=mq-about を使用するためのアダプタを提供する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst**
    - `1 で設定した、 WmqMessagingProvider を messaging_context_handler に設定する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst**
    - `分散トランザクションに対応したデータベース接続を生成するファクトリクラスを定義する。 |br|`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/jsr310_adaptor.rst**
    - `このアダプタを使用することで、 bean_util でJSR310(Date and Time API)を使用できる。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/jsr310_adaptor.rst**
    - `repository のコンポーネント設定ファイルに以下を追加することで、本機能が有効になる。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/log_adaptor.rst**
    - ``ログ出力機能 <log>` の設定ファイル(\ log.properties\ )にファクトリを設定する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst**
    - `extdoc:`Transactional<nablarch.integration.doma.Transactional>` インターセプタを設定する`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst**
    - `extdoc:`DomaDaoRepository#get<nablarch.integration.doma.DomaDaoRepository.get(java.lang.Class)>` を使用してDaoの実装クラスをルックアップする`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst**
    - `extdoc:`Transactional<nablarch.integration.doma.Transactional>` インターセプタによって開始されたトランザクションではなく、`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/router_adaptor.rst**
    - `extdoc:`RoutesMapping <nablarch.integration.router.RoutesMapping>` を初期化対象のリストに設定する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/router_adaptor.rst**
    - `| Path アノテーションによるルーティングを使用するには、 PathOptionsProviderRoutesMapping の pathOptionsProvider プロパティに JaxRsPathOptionsProvider を設定する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/router_adaptor.rst**
    - `| （methodBinderFactory プロパティの設定については jaxrs_adaptor を参照）`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst**
    - `さらに、 repository-overwrite_environment_configuration_by_os_env_var で説明している方法を用いることで、実行環境ごとに接続先のRedisを切り替えることができるようになる。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst**
    - ``ウェブのアーキタイプ <firstStepGenerateWebBlankProject>` でプロジェクトを生成している場合、デフォルトで session-store.xml を使用するように設定されているので、 session-store.xml のインポートを削除し、代わりに redisstore-lettuce.xml をインポートするように修正す`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst**
    - `この設定の説明については、 redisstore_initialize_client を参照。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/lettuce_adaptor/redishealthchecker_lettuce_adaptor.rst**
    - `ヘルスチェックについては health_check_endpoint_handler を参照。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/lettuce_adaptor/redishealthchecker_lettuce_adaptor.rst**
    - `ヘルスチェックは、 health_check_endpoint_handler-add_health_checker で説明している`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/lettuce_adaptor/redishealthchecker_lettuce_adaptor.rst**
    - `extdoc:`HealthChecker <nablarch.fw.web.handler.health.HealthChecker>` を継承したクラスを作成して追加できる。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/beforeFirstStep.rst**
    - `プロジェクト構成を検討する際には、 mavenModuleStructuresModuleDivisionPolicy を参照してからプロジェクト構成を検討すること。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/beforeFirstStep.rst**
    - `まだ設定していない場合は、 mvnSetting を参照して設定すること。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/addin_gsp.rst**
    - `POMの設定例は、 customizeDB_pom_dependencies を参照。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/maven.rst**
    - `以下参照してインストールを行う。インストールするバージョンは、 firstStepPreamble を参照。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/CustomizeDB.rst**
    - `OS環境変数で設定を上書きする方法については、 repository-overwrite_environment_configuration_by_os_env_var を参照。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/CustomizeDB.rst**
    - `dependency要素内の各要素については、customizeDBProfiles と同じように記述する。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/CustomizeDB.rst**
    - `使用するDialectクラスは、customizeDBWebComponentConfiguration と同一である。`
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/configuration/index.rst**
    - ``デフォルト設定一覧.xlsx <デフォルト設定一覧.xlsx>``
- **.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/mail.rst**
    - ``常駐バッチ<nablarch_batch-resident_batch>` を使い非同期にメールを送信する。`