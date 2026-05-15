**結論**: Nablarch 5からNablarch 6へのバージョンアップでは、Jakarta EE 10対応として主に「依存関係（pom.xml）の変更」「javax → jakarta 名前空間の一括置換」「設定ファイルのスキーマ更新」「ツールの差し替え」の4種類の変更がアプリケーションに必要となります。

**根拠**:

### 1. NablarchのBOMバージョン変更

pom.xml でNablarch BOMのバージョンを `6u2` に変更します。

### 2. Java EEのAPIをJakarta EEのAPIに置き換える

pom.xml に記載されているJava EE APIの依存関係を、それぞれJakarta EE版に変更します。代表例：

| 変更前 (groupId/artifactId) | 変更後 (groupId/artifactId) |
|---|---|
| javax.servlet:javax.servlet-api | jakarta.servlet:jakarta.servlet-api |
| javax.servlet.jsp:javax.servlet.jsp-api | jakarta.servlet.jsp:jakarta.servlet.jsp-api |
| javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api | jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api |
| org.apache.geronimo.specs:geronimo-jpa_2.0_spec | jakarta.persistence:jakarta.persistence-api |
| javax.ws.rs:javax.ws.rs-api | jakarta.ws.rs:jakarta.ws.rs-api |
| javax.annotation:javax.annotation-api | jakarta.annotation:jakarta.annotation-api |

### 3. 実装ライブラリの更新

| 対象 | 変更前 | 変更後 |
|---|---|---|
| Bean Validation | org.hibernate:hibernate-validator:5.3.6.Final | org.hibernate.validator:hibernate-validator:8.0.0.Final |
| JSTL実装 | taglibs:standard | org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0 |
| JAX-RS (Jersey) | jersey-bom（旧版） | org.glassfish.jersey:jersey-bom:3.1.8 |
| JMS | org.apache.activemq:activemq-all | artemis-server/artemis-jakarta-server/artemis-jakarta-client (各2.37.0) |

### 4. javax名前空間 → jakarta名前空間の変更

Javaソースコードのimport文や、JSP・設定ファイル内のすべての javax.*（Java EEに属するもの）を jakarta.* に置換する必要があります。プロジェクト全体をjavaxでGrep検索し、Java EE由来かどうかを判断したうえで置換します。

### 5. XMLスキーマの変更（web.xml など）

web.xmlのスキーマをJakarta EE 10対応版（version="6.0"、xmlns="https://jakarta.ee/xml/ns/jakartaee"）に変更します。

### 6. JSPのタグライブラリネームスペースの変更

`http://java.sun.com/jsp/jstl/core` を `jakarta.tags.core` に変更します。

### 7. ツールの差し替え

| 対象 | 変更内容 |
|---|---|
| waitt-maven-plugin | Jakarta EE非対応のため jetty-ee10-maven-plugin:12.0.12 に変更 |
| nablarch-testing-jetty6 | nablarch-testing-jetty12 に変更し、コンポーネント定義も HttpServerFactoryJetty12 に変更 |
| gsp-dba-maven-plugin | バージョンを 5.1.0 に更新（Jakarta EE対応版） |
| Domaアダプタ | 依存関係設定の更新が必要 |
| Micrometerアダプタ | Micrometerモジュールのバージョン更新が必要 |

### 8. Jakarta Batchアプリケーション（JSR352）の追加対応

JBeretと関連ライブラリをJakarta EE対応版に一括更新（jberet-core:2.1.4.Final、weld-core-impl:5.0.1.Final等）が必要です。

**注意点**:

- 後方互換性が維持されないため、Jakarta EE 10対応のアプリケーションサーバが必要です
- Java 17以上が必要です
- javax でGrep検索した際、javax.crypto.* 等のJava標準ライブラリはJava EEとは無関係のため置換しないでください
- 移行手順はNablarch 5の最新版への更新が完了していることを前提としています
- 6u3以降へバージョンアップする場合は、各リリースノートも確認してください

参照: about/migration/migration-migration.json#s2, #s5, #s7, #s9〜#s15, #s16〜#s20, #s21〜#s25, #s26, #s27, #s28, #s29, #s33