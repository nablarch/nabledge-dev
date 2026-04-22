# Transform rules (v6) — derived from source/JSON pairs

Stats per inline pattern:

| Pattern | Verbatim | Transformed/Dropped |
|---|---:|---:|
| role_target | 0 | 2902 |
| role_simple | 0 | 5039 |
| double_backtick | 6 | 2442 |
| ext_link_named | 0 | 282 |
| ext_link_anon | 0 | 4 |
| ref_named | 0 | 103 |
| substitution | 14 | 373 |
| footnote_ref | 198 | 0 |
| strong | 285 | 0 |
| emphasis | 105 | 1 |
| interpreted | 327 | 198 |

## role_target

### Sample transformations

- **transformed** `:javadoc_url:`DaoContext <nablarch-all/NablarchApi/nablarch/common/dao/DaoContext.html>`` (.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst)
  - MD context: `うかで判断できる。 例えば、 DaoContext はクラスに `@Published(tag="architect")` が記載されているためアーキテクト向けの公開APIであることが分かる。 一方で、 BasicDaoContextのfindAllメソッド `
- **transformed** `:javadoc_url:`BasicDaoContextのfindAllメソッド <nablarch-all/NablarchApi/nablarch/common/dao/BasicDaoContext.html#findAll(java.lang.Class)>`` (.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst)
  - MD context: `あることが分かる。 一方で、 BasicDaoContextのfindAllメソッド はクラスにもメソッドにも `@Published` が記載されていないことから非公開APIであることが分かる。 なお、公開APIに関する仕様の詳細は versionup_po`
- **transformed** `:java:extdoc:`Published <nablarch.core.util.annotation.Published>`` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `対象にしています。 Nablarchが定める公開APIは、 `Published` アノテーションが付与されたAPIになります。 クラスの全APIを公開する場合はクラス宣言に、 個別にメソッドを公開する場合はメソッド宣言に `Published` アノテーショ`
- **transformed** `:ref:`許可していないAPIが使用されていないかチェックする <api-analysis>`` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `運用してください。 ツールの詳細は、 許可していないAPIが使用されていないかチェックする  を参照してください。\n> **Tip:** Publishedアノテーションを付与する際は、アーキテクト向けとアプリケーションプログラマ向けに分類しています。\n\n* `
- **transformed** `:ref:`使用するNablarchのバージョン <beforefirstStepSpecityNablarchVer>`` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `性維持の方針により フレームワークは、基本的に、 使用するNablarchのバージョン の差し替えと設定ファイルの変更のみでバージョンアップできます。\n後方互換性の例外\n下記内容に該当する場合は、後方互換性が維持されないバージョンアップを行う場合があります。\n`
- **transformed** `:ref:`リリースノート<release-notes>`` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `施できない場合。\n\nなお、後方互換性が維持されない変更になる場合は リリースノート の「システムへの影響の可能性の内容と対処」列にその内容と移行方法を明記します。`
- **transformed** `:ref:`実行制御基盤 <runtime_platform>`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `Example\nExampleは、Nablarchアプリケーションフレームワークの機能の使用方法を示した実装例であり、 実行制御基盤 毎に作成している。\n本章では、Exampleに必要な環境構築手順と、アプリケーションの実行手順を解説する。\n\n> **Ti`
- **transformed** `:ref:`解説 <getting_started>`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `P)](https://github.com/nablarch/nablarch-example-web) (解説)\n- [ウェブアプリケーション (Thymeleaf)](https://github.com/nablarch/nablarch-exampl`
- **transformed** `:ref:`解説 <web_thymeleaf_adaptor>`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `f)](https://github.com/nablarch/nablarch-example-thymeleaf-web) (解説)\nウェブサービス\n- [RESTfulウェブサービス](https://github.com/nablarch/nablar`
- **transformed** `:ref:`解説 <rest_getting_started>`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `ビス](https://github.com/nablarch/nablarch-example-rest) (解説)\n- [HTTPメッセージング (受信)](https://github.com/nablarch/nablarch-example-http`

### Source-only (tokens not found in output, no nearby anchor)

- `:doc:`Jakarta RESTful Web Servicesサポート <../application_framework/application_framework/web_service/rest/architecture>`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`Jakarta RESTful Web Servicesサポート <../application_framework/application_framework/web_service/rest/architecture>``
- `:javadoc_url:`Nablarch APIドキュメント <nablarch-all/NablarchApi/>`` (.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst)
  - line: `* :javadoc_url:`Nablarch APIドキュメント <nablarch-all/NablarchApi/>``
- `:javadoc_url:`Nablarch Testing APIドキュメント <nablarch-testing/NablarchTestingApi/>`` (.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst)
  - line: `* :javadoc_url:`Nablarch Testing APIドキュメント <nablarch-testing/NablarchTestingApi/>``
- `:download:`全リリースノート一括ダウンロード <./nablarch-6-OSS-all-releasenote.zip>`` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
  - line: `:download:`全リリースノート一括ダウンロード <./nablarch-6-OSS-all-releasenote.zip>``
- `:download:`リリースノート(6u3) <./nablarch6u3-releasenote.xlsx>`` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
  - line: `- :download:`リリースノート(6u3) <./nablarch6u3-releasenote.xlsx>``
- `:download:`リリースノート(6u2) <./nablarch6u2-releasenote.xlsx>`` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
  - line: `- :download:`リリースノート(6u2) <./nablarch6u2-releasenote.xlsx>``
- `:download:`リリースノート(6u1) <./nablarch6u1-releasenote.xlsx>`` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
  - line: `- :download:`リリースノート(6u1) <./nablarch6u1-releasenote.xlsx>``
- `:download:`リリースノート(6) <./nablarch6-releasenote.xlsx>`` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
  - line: `- :download:`リリースノート(6) <./nablarch6-releasenote.xlsx>``
- `:download:`LICENSE.txt <./LICENSE.txt>`` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/license.rst)
  - line: `:download:`LICENSE.txt <./LICENSE.txt>``
- `:java:extdoc:`Published <nablarch.core.util.annotation.Published>`` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - line: `:java:extdoc:`Published <nablarch.core.util.annotation.Published>``

## role_simple

### Sample transformations

- **transformed** `:ref:`waitt-to-jetty`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `内容を説明する。\n\nプロジェクトによっては不要な手順が含まれる可能性があるが、その場合は適宜取捨選択して読み進めること（例えば、 waitt-maven-pluginをjetty-ee10-maven-pluginに変更する や nablarch-testin`
- **transformed** `:ref:`update-ntf-jetty`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>\n```\n**修正後**\n\n```jsp\n<%@ taglib prefix="c" uri="jakarta.tags.core" %`
- **transformed** `:ref:`java_ee_jakarta_ee_comparation`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `ment>\n```\nまた、ここで記載されていない依存関係を変更するための参考として、本ページ末尾の付録に Java EEとJakarta EEの仕様の対応表 を記載する。\nJakarta EEでの `dependency` が何になるかは各仕様のページに記載さ`
- **transformed** `:ref:`doma_dependency`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `設定が必要となる。\n詳細については doma_dependency を参照のこと。\n\nまた、新しいバージョンで推奨する実装方法についても案内しているため、必要に応じて対応する。\n詳細については migration_doma2.44.0 を参照のこと。\n\n###`
- **transformed** `:ref:`migration_doma2.44.0`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `設定が必要となる。\n詳細については doma_dependency を参照のこと。\n\nまた、新しいバージョンで推奨する実装方法についても案内しているため、必要に応じて対応する。\n詳細については migration_doma2.44.0 を参照のこと。\n\n###`
- **transformed** `:ref:`micrometer_collaboration`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `設定が必要となる。\n詳細については doma_dependency を参照のこと。\n\nまた、新しいバージョンで推奨する実装方法についても案内しているため、必要に応じて対応する。\n詳細については migration_doma2.44.0 を参照のこと。\n\n###`
- **transformed** `:ref:`java_ee_jakarta_ee_comparation`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `には判断できない。\n本ページ付録の Java EEとJakarta EEの仕様の対応表 に各仕様の名前空間を記載しているので、これを参考にヒットした `javax` がJava EEのものか判断すること。\n\nJava EEの名前空間であると判断できた場合は、 `
- **transformed** `:doc:`../application_framework/application_framework/batch/jsr352/index`` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `順で移行できる。\n\nただし ../application_framework/application_framework/batch/jsr352/index のみ、JSR352に準拠した実装として使用しているJBeretと関連するライブラリの更新が複雑である`
- **transformed** `:doc:`../application_framework/application_framework/libraries/validation/bean_validation`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - MD context: `footnote]\n「BeanValidation」はNablarchが提供するバリデーション機能である ../application_framework/application_framework/libraries/validation/bean_vali`
- **transformed** `:javadoc_url:`DaoContext <nablarch-all/NablarchApi/nablarch/common/dao/DaoContext.html>`` (.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst)
  - MD context: `うかで判断できる。 例えば、 DaoContext はクラスに `@Published(tag="architect")` が記載されているためアーキテクト向けの公開APIであることが分かる。 一方で、 BasicDaoContextのfindAllメソッド `

### Source-only (tokens not found in output, no nearby anchor)

- `:doc:`../application_framework/application_framework/handlers/rest/jaxrs_bean_validation_handler`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`../application_framework/application_framework/handlers/rest/jaxrs_bean_validation_handler` [#jaxr_rs_bean_validation_handler_footnote]_`
- `:doc:`../application_framework/adaptors/jaxrs_adaptor`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`../application_framework/adaptors/jaxrs_adaptor``
- `:doc:`Jakarta RESTful Web Servicesサポート <../application_framework/application_framework/web_service/rest/architecture>`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`Jakarta RESTful Web Servicesサポート <../application_framework/application_framework/web_service/rest/architecture>``
- `:doc:`../application_framework/application_framework/handlers/rest/jaxrs_response_handler`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`../application_framework/application_framework/handlers/rest/jaxrs_response_handler``
- `:doc:`../application_framework/application_framework/libraries/tag`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`../application_framework/application_framework/libraries/tag``
- `:doc:`../development_tools/toolbox/JspStaticAnalysis/index`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`../development_tools/toolbox/JspStaticAnalysis/index``
- `:doc:`../application_framework/application_framework/batch/jsr352/index`` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
  - line: `- :doc:`../application_framework/application_framework/batch/jsr352/index``
- `:javadoc_url:`Nablarch APIドキュメント <nablarch-all/NablarchApi/>`` (.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst)
  - line: `* :javadoc_url:`Nablarch APIドキュメント <nablarch-all/NablarchApi/>``
- `:javadoc_url:`Nablarch Testing APIドキュメント <nablarch-testing/NablarchTestingApi/>`` (.lw/nab-official/v6/nablarch-document/ja/nablarch_api/index.rst)
  - line: `* :javadoc_url:`Nablarch Testing APIドキュメント <nablarch-testing/NablarchTestingApi/>``
- `:download:`全リリースノート一括ダウンロード <./nablarch-6-OSS-all-releasenote.zip>`` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
  - line: `:download:`全リリースノート一括ダウンロード <./nablarch-6-OSS-all-releasenote.zip>``

## double_backtick

### Sample transformations

- **transformed** ```javax.*``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `akarta EE 9で名前空間が `javax.*` から `jakarta.*` になるという大きな変更が入っている。\n\nしたがって、Nablarch 5で作られたプロジェクトでNablarch 6へ移行するためには、Nablarchのバージョンアップだけ`
- **transformed** ```jakarta.*``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: ` 9で名前空間が `javax.*` から `jakarta.*` になるという大きな変更が入っている。\n\nしたがって、Nablarch 5で作られたプロジェクトでNablarch 6へ移行するためには、Nablarchのバージョンアップだけでなくプロジェクト`
- **transformed** ```pom.xml``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `ンアップができる。\n以下のように、 `pom.xml` でNablarchのBOMを読み込んでいる部分の `<version>` を変更する。\n\n```xml\n<dependencyManagement>\n  <dependencies>\n    <depen`
- **transformed** ```<version>``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: ``pom.xml` でNablarchのBOMを読み込んでいる部分の `<version>` を変更する。\n\n```xml\n<dependencyManagement>\n  <dependencies>\n    <dependency>\n      <grou`
- **transformed** ```dependency``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `更する\n\nJava EEのAPIの依存関係(`dependency`)を、Jakarta EEのものに変更する必要がある。\n例えば代表的なものとしては、Java Servletなどが挙げられる。\n\nただ、Java EEのAPIの `dependency` は、`
- **transformed** ```dependency``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `更する\n\nJava EEのAPIの依存関係(`dependency`)を、Jakarta EEのものに変更する必要がある。\n例えば代表的なものとしては、Java Servletなどが挙げられる。\n\nただ、Java EEのAPIの `dependency` は、`
- **transformed** ```groupId``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `統一されていない。\nこのため、 `groupId` などから機械的に判断はできない。\nどの `dependency` がJava EEのAPIなのかは、 `groupId` や `artifactId` 、jarの中に含まれるクラスなどから判断しなければならな`
- **transformed** ```dependency``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `\n\n```xml\n<dependencyManagement>\n  <dependencies>\n    <dependency>\n      <groupId>com.nablarch.profile</groupId>\n      <artifactId>`
- **transformed** ```groupId``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `cy` がJava EEのAPIなのかは、 `groupId` や `artifactId` 、jarの中に含まれるクラスなどから判断しなければならない。\n\n参考までに、Nablarchが提供しているアーキタイプやExampleでの変更内容を以下に記載する。\n`
- **transformed** ```artifactId``` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `y>\n      <groupId>com.nablarch.profile</groupId>\n      <artifactId>nablarch-bom</artifactId>\n      <version>6u2</version>\n      <t`

### Source-only (tokens not found in output, no nearby anchor)

- ```1``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst)
  - line: `2. ``1`` で設定した、 ``WmqMessagingProvider`` を :ref:`messaging_context_handler` に設定する。`
- ```1``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst)
  - line: `3. ``1`` で設定した、 ``WmqMessagingProvider`` は初期化が必要なので初期化対象のリストに設定する。`
- ```2``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst)
  - line: `3. ``2`` で定義したファクトリクラスを、 :ref:`database_connection_management_handler` に設定する。`
- ```4``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst)
  - line: `5. ``4`` で定義したファクトリクラスを :ref:`transaction_management_handler` に設定する。`
- ```PK``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/mail.rst)
  - line: `* - 連番 ``PK```
- ```PK``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/mail.rst)
  - line: `* - 連番 ``PK```
- ```PK``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/mail.rst)
  - line: `* - 言語 ``PK```
- ```\n``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/log.rst)
  - line: ```\n`` と ``\t`` という文字列は出力できない。`
- ```\t``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/log.rst)
  - line: ```\n`` と ``\t`` という文字列は出力できない。`
- ```<b>``` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/tag.rst)
  - line: ```<b>`` や ``<del>`` のような装飾系のHTMLタグをエスケープせずに出力するカスタムタグ。`

## ext_link_named

### Sample transformations

- **transformed** ``Nablarch 5のリリースノート <https://nablarch.github.io/docs/5-LATEST/doc/releases/index.html>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `\nNablarch 5の最新版へのバージョンアップに必要となる修正内容については、 [Nablarch 5のリリースノート](https://nablarch.github.io/docs/5-LATEST/doc/releases/index.html) を`
- **transformed** ``Nablarch 5のセットアップ手順 <https://nablarch.github.io/docs/5-LATEST/doc/application_framework/application_framework/blank_project/FirstStep.html>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `対応も必要となる。 対応に必要となる修正内容については、 [Nablarch 5のセットアップ手順](https://nablarch.github.io/docs/5-LATEST/doc/application_framework/application_`
- **transformed** ``Jakarta Servlet 6.0 の仕様のページ (外部サイト、英語) <https://jakarta.ee/specifications/servlet/6.0/#details>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `択して読み進めること（例えば、 waitt-maven-pluginをjetty-ee10-maven-pluginに変更する や nablarch-testing-jetty6をnablarch-testing-jetty12に変更する はウェブプロジェクト`
- **transformed** ``Jakarta RESTful Web Services 3.1 の仕様のページ (外部サイト、英語) <https://jakarta.ee/specifications/restful-ws/3.1/#compatible-implementations>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `も参考にすること。\n(例えば、 [Jakarta RESTful Web Services 3.1 の仕様のページ (外部サイト、英語)](https://jakarta.ee/specifications/restful-ws/3.1/#compatible`
- **transformed** ``Nablarch 5のセットアップ手順 <https://nablarch.github.io/docs/5-LATEST/doc/application_framework/application_framework/blank_project/FirstStep.html>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `バージョンとなる。 そのため、ここで説明する手順は、Nablarch 5の最新バージョンからNablarch 6u2へのバージョンアップを前提としている。 またアーキタイプから作ったプロジェクトなどに組み込まれているgsp-dba-maven-pluginは、`
- **transformed** ``dependency:tree <https://maven.apache.org/plugins/maven-dependency-plugin/tree-mojo.html>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `いる場合がある。 [dependency:tree](https://maven.apache.org/plugins/maven-dependency-plugin/tree-mojo.html) 等により依存関係を確認し、更新もしくは削除を判断すること。\n`
- **transformed** ``gsp-dba-maven-plugin (外部サイト) <https://github.com/coastland/gsp-dba-maven-plugin>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `ginを更新する\n\nnablarch-example-webをはじめ、アーキタイプから作ったプロジェクトには [gsp-dba-maven-plugin (外部サイト)](https://github.com/coastland/gsp-dba-maven-p`
- **transformed** ``Java 17での設定ガイド (外部サイト) <https://github.com/coastland/gsp-dba-maven-plugin/tree/4.x.x-main?tab=readme-ov-file#java17%E3%81%A7%E3%81%AE%E8%A8%AD%E5%AE%9A>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `ジョンではJava 17で使用するために [Java 17での設定ガイド (外部サイト)](https://github.com/coastland/gsp-dba-maven-plugin/tree/4.x.x-main?tab=readme-ov-file`
- **transformed** ``gsp-dba-maven-pluginのガイド (外部サイト) <https://github.com/coastland/gsp-dba-maven-plugin?tab=readme-ov-file#generate-entity>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `設定が必要となる。\n詳細については doma_dependency を参照のこと。\n\nまた、新しいバージョンで推奨する実装方法についても案内しているため、必要に応じて対応する。\n詳細については migration_doma2.44.0 を参照のこと。\n\n###`
- **transformed** ``waitt-maven-plugin (外部サイト、英語) <https://github.com/kawasima/waitt>`_` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: `ginに変更する\n\nnablarch-example-webをはじめ、アーキタイプから作ったウェブアプリケーションのプロジェクトには [waitt-maven-plugin (外部サイト、英語)](https://github.com/kawasima/wai`

## ext_link_anon

### Sample transformations

- **transformed** ``Nablarchシステム開発ガイド(外部サイト) <https://fintan.jp/page/252/>`__` (.lw/nab-official/v6/nablarch-document/ja/external_contents/index.rst)
  - MD context: `に含まれている）。\nNablarchシステム開発ガイド\nNablarchシステム開発ガイドは、Nablarchを使ってシステムを開発するエンジニアに対して、開発開始前・開発中にすべきこと、参照すべきものを示すガイドである。\nNablarchを使ったシステム開発`
- **transformed** ``開発標準(外部サイト) <https://fintan.jp/page/1868/#development-standards>`__` (.lw/nab-official/v6/nablarch-document/ja/external_contents/index.rst)
  - MD context: `認できる。\n\n| [開発標準(外部サイト)](https://fintan.jp/page/1868/#development-standards)`
- **transformed** ``Plausible Analytics <https://plausible.io>`__` (.lw/nab-official/v6/nablarch-document/ja/terms_of_use/index.rst)
  - MD context: `。\n情報の利用目的\n取得した情報はアクセス解析に利用されます。\nページのアクセス数等からサイトの利用状況を把握し、サイトの改善に利用します。\nアクセス情報は匿名で収集され、個人を特定することはできません。\n情報の送信先\n取得した情報は [Plausible A`
- **transformed** ``Plausible Analyticsのポリシー <https://plausible.io/data-policy>`__` (.lw/nab-official/v6/nablarch-document/ja/terms_of_use/index.rst)
  - MD context: `す [4]_。 |\nより詳細な情報については、 [Plausible Analyticsのポリシー](https://plausible.io/data-policy) をご参照ください。\n\n.. [1]\nユーザーエージェントから取得しますが、必要な情報だけを`

## ref_named

### Sample transformations

- **transformed** ``LoggingMeterRegistry(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `を提供している。\n\nここでは、 [LoggingMeterRegistry(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/in`
- **transformed** ``LoggingMeterRegistry(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `。\n\nここでは、 [LoggingMeterRegistry(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/instrumen`
- **transformed** ``LoggingMeterRegistry(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `どの手間がかかる。 このため、この説明では最も簡単に動作を確認できる [LoggingMeterRegistry(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io`
- **transformed** ``MeterBinder(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `ントとして宣言する\nMicrometerには、 [MeterBinder(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/ins`
- **transformed** ``JvmMemoryMetrics(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `め用意されている。\n（例：JVMのメモリ使用量は [JvmMemoryMetrics(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/co`
- **transformed** ``ProcessorMetrics(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `ics.html) 、CPU使用率は [ProcessorMetrics(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/ins`
- **transformed** ``MeterBinder(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `ある。\n本アダプタでは、このレジストリを システムリポジトリ に登録するための `ComponentFactory` を提供している。\n\nここでは、 [LoggingMeterRegistry(外部サイト、英語)](https://javadoc.io/doc`
- **transformed** ``SimpleMeterRegistry(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `-|---|\n| [SimpleMeterRegistry(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/instrument`
- **transformed** ``LoggingMeterRegistry(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `。\n\nここでは、 [LoggingMeterRegistry(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-core/1.13.0/io/micrometer/core/instrumen`
- **transformed** ``CloudWatchMeterRegistry(外部サイト、英語)`_` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/micrometer_adaptor.rst)
  - MD context: `` 以上 |\n| [CloudWatchMeterRegistry(外部サイト、英語)](https://javadoc.io/doc/io.micrometer/micrometer-registry-cloudwatch2/1.13.0/io/microm`

## substitution

### Sample transformations

- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `ージョンアップ | アプリケーションフレームワークに対する大規模な機能追加・変更を伴う機能変更を行います。   例）  ・実行制御基盤の刷新 | アプリケーションフレームワーク  開発ツール  開発標準 | １年～ |\n| リビジョンアップ | 不具合対応、機`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `ージョンアップ | アプリケーションフレームワークに対する大規模な機能追加・変更を伴う機能変更を行います。   例）  ・実行制御基盤の刷新 | アプリケーションフレームワーク  開発ツール  開発標準 | １年～ |\n| リビジョンアップ | 不具合対応、機`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `ンフレームワーク  開発ツール  開発標準 | １年～ |\n| リビジョンアップ | 不具合対応、機能追加・変更を行います。  例）  ・Java最新版対応  ・開発標準の追加/変更  | 同上 | 半期 [#release_schedule_for_bugs`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `います。  例）  ・Java最新版対応  ・開発標準の追加/変更  | 同上 | 半期 [#release_schedule_for_bugs_revision_up]_ |\n| バグフィックス | セキュリティ・運用レベルに致命的な影響を与える、緊急性が高`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `ava最新版対応  ・開発標準の追加/変更  | 同上 | 半期 [#release_schedule_for_bugs_revision_up]_ |\n| バグフィックス | セキュリティ・運用レベルに致命的な影響を与える、緊急性が高いアプリケーションフレー`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `クトバージョン番号\nマイナーバージョンアップ時にインクリメントされます。 \n例）Nablarch 6u6 → Nablarch 7 \n開始番号は5です。\n\nアップデート番号\nリビジョンアップまたはバグフィックス時にインクリメントされます。 \n例）Nablarc`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `Nablarch のバージョンアップ方針\nNablarchが提供する コンテンツに対するバージョンアップ方針について説明します。\nリリース単位\nNablarchはバージョン単位でリリースします。\nバージョンは、複数モジュールの組み合わせで構`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: `\nアップデート番号\nリビジョンアップまたはバグフィックス時にインクリメントされます。 \n例）Nablarch 6u6 → Nablarch 6u7 \n開始番号は0です。ただし、番号0の場合はアップデート番号は付けられません。\n後方互換性ポリシー\nNablarc`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - MD context: ` Nablarch 6u7 \n開始番号は0です。ただし、番号0の場合はアップデート番号は付けられません。\n後方互換性ポリシー\nNablarchの後方互換性ポリシーについて説明します。\n後方互換性を維持する範囲\nアプリケーションフレームワークとテスティングフレー`
- **transformed** `|br|` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst)
  - MD context: `定義する。\n\n2. 分散トランザクションに対応したデータベース接続を生成するファクトリクラスを定義する。 \n(`nablarch.integration.messaging.wmq.xa.WmqXADbConnectionFactoryForXADataSou`

### Source-only (tokens not found in output, no nearby anchor)

- `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - line: `.. |br| raw:: html`
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - line: `|br|`
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - line: `例） |br|`
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - line: `|br|`
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
  - line: `例） |br|`
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/webspheremq_adaptor.rst)
  - line: `.. |br| raw:: html`
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/functional_comparison.rst)
  - line: `- ○ |br| :ref:`解説書へ <main-option_parameter>``
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/functional_comparison.rst)
  - line: `- ○ |br| :java:extdoc:`Javadocへ <nablarch.fw.batch.ee.listener.job.DuplicateJobRunningCheckListener>``
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/functional_comparison.rst)
  - line: `- ○ |br| :ref:`解説書へ <duplicate_process_check_handler>``
- `|br|` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/batch/functional_comparison.rst)
  - line: `- ○ |br| :ref:`解説書へ <process_stop_handler>``

## footnote_ref

### Sample transformations

- **verbatim** `[#jaxr_rs_bean_validation_handler_footnote]_` (.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst)
- **verbatim** `[1]_` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
- **verbatim** `[1]_` (.lw/nab-official/v6/nablarch-document/ja/releases/index.rst)
- **verbatim** `[1]_` (.lw/nab-official/v6/nablarch-document/ja/terms_of_use/index.rst)
- **verbatim** `[2]_` (.lw/nab-official/v6/nablarch-document/ja/terms_of_use/index.rst)
- **verbatim** `[3]_` (.lw/nab-official/v6/nablarch-document/ja/terms_of_use/index.rst)
- **verbatim** `[4]_` (.lw/nab-official/v6/nablarch-document/ja/terms_of_use/index.rst)
- **verbatim** `[#release_schedule_for_bugs_revision_up]_` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
- **verbatim** `[#release_schedule_for_bugs_bug_fix]_` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst)
- **verbatim** `[1]_` (.lw/nab-official/v6/nablarch-document/ja/about_nablarch/concept.rst)

## strong

### Sample transformations

- **verbatim** `**修正前**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正後**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正前**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正後**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正前**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正後**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正前**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正後**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正前**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
- **verbatim** `**修正後**` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)

## emphasis

### Sample transformations

- **transformed** `*`` から ``jakarta.*` (.lw/nab-official/v6/nablarch-document/ja/migration/index.rst)
  - MD context: ` 9で名前空間が `javax.*` から `jakarta.*` になるという大きな変更が入っている。\n\nしたがって、Nablarch 5で作られたプロジェクトでNablarch 6へ移行するためには、Nablarchのバージョンアップだけでなくプロジェクト`
- **verbatim** `*Local#getLanguage()*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/code.rst)
- **verbatim** `*jakarta.persistence.Entity*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)
- **verbatim** `*jakarta.persistence.Table*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)
- **verbatim** `*jakarta.persistence.Access*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)
- **verbatim** `*jakarta.persistence.Column*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)
- **verbatim** `*jakarta.persistence.Id*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)
- **verbatim** `*jakarta.persistence.Version*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)
- **verbatim** `*jakarta.persistence.Temporal*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)
- **verbatim** `*java.util.Date*` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/database/universal_dao.rst)

## interpreted

### Sample transformations

- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `P)](https://github.com/nablarch/nablarch-example-web) (解説)\n- [ウェブアプリケーション (Thymeleaf)](https://github.com/nablarch/nablarch-exampl`
- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `f)](https://github.com/nablarch/nablarch-example-thymeleaf-web) (解説)\nウェブサービス\n- [RESTfulウェブサービス](https://github.com/nablarch/nablar`
- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `ビス](https://github.com/nablarch/nablarch-example-rest) (解説)\n- [HTTPメッセージング (受信)](https://github.com/nablarch/nablarch-example-http`
- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `信)](https://github.com/nablarch/nablarch-example-http-messaging) (解説)\n- [HTTPメッセージング (送信)](https://github.com/nablarch/nablarch-ex`
- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `信)](https://github.com/nablarch/nablarch-example-http-messaging-send) (解説)\nバッチアプリケーション\n- [Jakarta Batchに準拠したバッチアプリケーション](https://g`
- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `ョン](https://github.com/nablarch/nablarch-example-batch-ee) (解説)\n- [Nablarchバッチアプリケーション](https://github.com/nablarch/nablarch-examp`
- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `ョン](https://github.com/nablarch/nablarch-example-batch-ee) (解説)\n- [Nablarchバッチアプリケーション](https://github.com/nablarch/nablarch-examp`
- **transformed** ``_ (:ref:`` (.lw/nab-official/v6/nablarch-document/ja/examples/index.rst)
  - MD context: `ング](https://github.com/nablarch/nablarch-example-db-queue) (解説)`
- **transformed** `` を :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/mail_sender_freemarker_adaptor.rst)
  - MD context: `   class="nablarch.integration.mail.freemarker.FreeMarkerMailProcessor" autowireType="None">\n  <property name="configuration">\n   `
- **transformed** ``_  で :ref:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/jaxrs_adaptor.rst)
  - MD context: `語)](https://eclipse-ee4j.github.io/jersey/)  で RESTfulウェブサービス を使用するためのアダプタ\n* [RESTEasy(外部サイト、英語)](https://resteasy.dev/) で RESTful`

### Source-only (tokens not found in output, no nearby anchor)

- `` を使用し、第2引数に :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst)
  - line: `その場合は、Daoの実装クラスをルックアップする際に :java:extdoc:`DomaDaoRepository#get(java.lang.Class,java.lang.Class)<nablarch.integration.doma.DomaDaoRepository.get(java.lang.Class,java.lang.Class)>` を使用し、第2引数に :java:extdoc:`DomaTransactionNotSupportedConfig<nablarch.integration.doma.DomaTransactionNotSupportedConfig>` のClassクラスを指定する。`
- `` を使用した場合は :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst)
  - line: `引数が1つの :java:extdoc:`DomaDaoRepository#get(java.lang.Class)<nablarch.integration.doma.DomaDaoRepository.get(java.lang.Class)>` を使用した場合は :java:extdoc:`DomaConfig<nablarch.integration.doma.DomaConfig>` が使用されるため、 :java:extdoc:`DomaTransactionItemWriteListener<nablarch.integration.doma.batch.ee.listener.DomaTransactionItemWriteListener>` によるトランザクションのコミットでストリームがクローズされるため、後続のレコードが読み込めなくなってしまう。`
- `` が使用されるため、 :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst)
  - line: `引数が1つの :java:extdoc:`DomaDaoRepository#get(java.lang.Class)<nablarch.integration.doma.DomaDaoRepository.get(java.lang.Class)>` を使用した場合は :java:extdoc:`DomaConfig<nablarch.integration.doma.DomaConfig>` が使用されるため、 :java:extdoc:`DomaTransactionItemWriteListener<nablarch.integration.doma.batch.ee.listener.DomaTransactionItemWriteListener>` によるトランザクションのコミットでストリームがクローズされるため、後続のレコードが読み込めなくなってしまう。`
- `` を使用し、第2引数に :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst)
  - line: `* Daoの実装クラスを取得する際に :java:extdoc:`DomaDaoRepository#get(java.lang.Class,java.lang.Class)<nablarch.integration.doma.DomaDaoRepository.get(java.lang.Class,java.lang.Class)>` を使用し、第2引数に :java:extdoc:`DomaTransactionNotSupportedConfig<nablarch.integration.doma.DomaTransactionNotSupportedConfig>` を指定する。`
- `` を使用する場合が該当する。(:ref:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst)
  - line: `例えば、 :ref:`メール送信ライブラリ <mail>` を使用する場合が該当する。(:ref:`メール送信要求 <mail-request>` で :ref:`database` を使用している。)`
- `` で :ref:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/doma_adaptor.rst)
  - line: `例えば、 :ref:`メール送信ライブラリ <mail>` を使用する場合が該当する。(:ref:`メール送信要求 <mail-request>` で :ref:`database` を使用している。)`
- `` を実装したクラスを作り、 :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/adaptors/router_adaptor.rst)
  - line: `ログのフォーマットを変更したい場合は、 :java:extdoc:`PathOptionsFormatter <nablarch.integration.router.PathOptionsFormatter>` を実装したクラスを作り、 :java:extdoc:`PathOptionsProviderRoutesMapping <nablarch.integration.router.PathOptionsProviderRoutesMapping>` の ``pathOptionsFormatter`` プロパティに設定する。`
- `` ( :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/mail.rst)
  - line: `* :java:extdoc:`MailUtil<nablarch.common.mail.MailUtil>` ( :java:extdoc:`MailRequester<nablarch.common.mail.MailRequester>` を取得する)`
- `` から取得した :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/message.rst)
  - line: `:java:extdoc:`MessageUtil <nablarch.core.message.MessageUtil>` から取得した :java:extdoc:`Message <nablarch.core.message.Message>` を元に業務例外( :java:extdoc:`ApplicationException <nablarch.core.message.ApplicationException>` )を生成し送出する。`
- `` や、 :java:extdoc:`` (.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/message.rst)
  - line: `複数の :java:extdoc:`Map <java.util.Map>` や、 :java:extdoc:`Map <java.util.Map>` 以外の値とセットで指定された場合は、`

## Directives

13 distinct directive names.
### .. code-block:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/migration/index.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/migration/index.rst*

```rst

```

### .. contents:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/migration/index.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst*

```rst

```

### .. csv-table:: (1 samples)

*.lw/nab-official/v6/nablarch-document/ja/development_tools/toolbox/SqlExecutor/SqlExecutor.rst*

```rst

```

### .. figure:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/development_tools/toolbox/SqlExecutor/SqlExecutor.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/development_tools/toolbox/SqlExecutor/SqlExecutor.rst*

```rst

```

### .. image:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/maven.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/mail.rst*

```rst

```

### .. important:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/migration/index.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/about_nablarch/versionup_policy.rst*

```rst

```

### .. java:method:: (1 samples)

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/web/getting_started/client_create/client_create1.rst*

```rst

```

### .. list-table:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/migration/index.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/jakarta_ee/index.rst*

```rst

```

### .. note:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerBatch.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWeb.rst*

```rst

```

### .. table:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/tag/tag_reference.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/libraries/tag/tag_reference.rst*

```rst

```

### .. tip:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/migration/index.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/migration/index.rst*

```rst

```

### .. toctree:: (5 samples)

*.lw/nab-official/v6/nablarch-document/ja/about_nablarch/index.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/biz_samples/index.rst*

```rst

```

### .. warning:: (4 samples)

*.lw/nab-official/v6/nablarch-document/ja/application_framework/application_framework/nablarch/architecture.rst*

```rst

```

*.lw/nab-official/v6/nablarch-document/ja/development_tools/toolbox/SqlExecutor/SqlExecutor.rst*

```rst

```
