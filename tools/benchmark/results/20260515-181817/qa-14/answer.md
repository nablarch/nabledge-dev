**結論**: Nablarch 5からNablarch 6へのバージョンアップでJakarta EE 10対応として必要なアプリケーションへの影響は、大きく「名前空間の変更（`javax.*` → `jakarta.*`）」「依存関係（pom.xml）の更新」「設定ファイルの変更」の3カテゴリに分類される。後方互換性は維持されないため、アプリケーションサーバもJakarta EE 10対応版が必要となる。

**根拠**:

**1. 前提条件**
- Java 17以上が必要（Nablarch 6モジュールはJava 17でコンパイル済み）
- Jakarta EE 10対応のアプリケーションサーバが必要
- 移行手順はNablarch 6u2への移行を前提としている

**2. Java EEの依存関係をJakarta EEに変更する（pom.xml）**

| 変更前（Java EE） | 変更後（Jakarta EE） |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

Jakarta EEのBOMを読み込んで個別バージョン指定を省略することを推奨：
```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**3. Java EE仕様の実装ライブラリを更新する**

| 変更前 | 変更後 |
|---|---|
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard`（JSTL実装） | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| Jersey BOM（JAX-RS実装） | Jersey BOM 3.1.8 |
| ActiveMQ `activemq-all`（JMS） | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client`（各 2.37.0） |

**4. Domaアダプタ・Micrometerアダプタの更新**
- Domaアダプタ使用時：依存関係の設定変更が必要
- Micrometerアダプタ使用時：連携しているMicrometerモジュールのバージョン更新が必要

**5. ビルド・テストプラグインの更新（ウェブプロジェクト）**
- `waitt-maven-plugin` → `org.eclipse.jetty.ee10:jetty-ee10-maven-plugin:12.0.12`
- `nablarch-testing-jetty6`（NTF） → `nablarch-testing-jetty12` に変更し、`HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` に変更

**6. `gsp-dba-maven-plugin` の更新**
- バージョン 5.1.0 に更新（Jakarta EEおよびNablarch 6u2対応）

**7. Javaソースコードの名前空間変更（`javax` → `jakarta`）**
- Jakarta EE 9で`javax.*`から`jakarta.*`へ変更。コンパイルエラーになる箇所だけでなく、文字列・JSP・設定ファイル内のすべての`javax`をGrep検索して判定・置換が必要。
- 例：`import javax.validation.ConstraintValidator` → `import jakarta.validation.ConstraintValidator`
- 注意：標準ライブラリの`javax.crypto.*`等はJava EE名前空間ではないため変更不要

**8. XMLスキーマの変更（web.xml等）**
```xml
<!-- 変更前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" ... version="3.1">
<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" ... version="6.0">
```

**9. JSPタグライブラリのネームスペース変更**
```jsp
<!-- 変更前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!-- 変更後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

**10. Jakarta Batchアプリケーション（JSR352）の追加手順**
JBeretおよび関連ライブラリの依存関係を全面的にJakarta EE対応版（`jakarta.batch:jakarta.batch-api`、`weld-core-impl:5.0.1.Final`、`jberet-core:2.1.4.Final` 等）に変更が必要。

**注意点**:
- 後方互換性は維持されないため、アプリケーションサーバのJakarta EE 10対応は必須
- `javax` でGrepしたすべての箇所が変更対象とは限らない（`javax.crypto` 等の標準ライブラリは対象外）
- 6u3以降へのバージョンアップは、6u3以降のリリースノートも順に参照して追加手順を確認すること
- Java 17対応のために既に追加していた依存関係は、Nablarch 6u2移行後に不要になる場合がある（`dependency:tree`で確認が必要）
- JSR352バッチ使用時、`slf4j-nablarch-adaptor`をLogbackより後にクラスパス配置しないと`NoClassDefFoundError`が発生する場合がある

参照: `about/migration/migration-migration.json#s2`, `about/migration/migration-migration.json#s3`, `about/migration/migration-migration.json#s5`, `about/migration/migration-migration.json#s7`, `about/migration/migration-migration.json#s9`〜`s29`, `about/migration/migration-migration.json#s31`, `about/about-nablarch/about-nablarch-jakarta-ee.json#s2`