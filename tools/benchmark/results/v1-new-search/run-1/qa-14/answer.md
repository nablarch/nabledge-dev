**結論**: Nablarch 5→6バージョンアップにおけるJakarta EE 10対応の最大の影響は、Javaソース・JSP・設定ファイル全体に及ぶ `javax.*` → `jakarta.*` 名前空間の変更と、Java EEのAPIライブラリをJakarta EE対応版へ置き換えることです。

**根拠**:

### 1. 名前空間の変更（`javax` → `jakarta`）

Jakarta EE 9で入った名前空間変更の対応が必要です。コンパイルエラーになる箇所だけでなく、文字列指定・JSP・設定ファイルも含めてプロジェクト全体をgrep検索して修正します。

```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

> **注意**: `javax.crypto.SecretKeyFactory` など標準ライブラリの `javax.*` は変更不要です。Java EE仕様のものかどうかを判断して置換してください。

### 2. 依存ライブラリの置き換え

**API（`pom.xml` の `dependency`）**

| 変更前 | 変更後 |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

BOM を使用することで個別バージョン管理が不要になります:

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**実装ライブラリ**

| 種別 | 変更前 | 変更後 |
|---|---|---|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL実装 | `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS実装(Jersey) | jersey-bom 旧バージョン | `jersey-bom:3.1.8` |
| JMS実装(ActiveMQ) | `activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` |

### 3. XMLスキーマの変更

`web.xml` 等のXMLファイルのスキーマ指定を Jakarta EE 10 のものに変更します。

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
         http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
         version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

### 4. JSP taglib ネームスペースの変更

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 5. ビルド・テストツールの変更（ウェブプロジェクト）

| 変更前 | 変更後 |
|---|---|
| `waitt-maven-plugin` | `jetty-ee10-maven-plugin:12.0.12` |
| `nablarch-testing-jetty6` | `nablarch-testing-jetty12` |
| `nablarch.fw.web.httpserver.HttpServerFactoryJetty6` | `HttpServerFactoryJetty12` |

### 6. Jakarta Batch固有の変更

JBeret と関連ライブラリの大幅更新が必要です。`jboss-batch-api_1.0_spec` → `jakarta.batch:jakarta.batch-api`、`weld-core` → `weld-core-impl:5.0.1.Final` 等、依存関係全体の置き換えが発生します。

**注意点**:
- Jakarta EE 10に対応しているアプリケーションサーバが必要です（後方互換性なし）
- Java 17以上が動作要件となります
- `gsp-dba-maven-plugin` を使用している場合は `5.1.0` への更新が必要（`generate-entity` で生成されるエンティティのアノテーションが `javax.*` → `jakarta.*` に変わる）
- 移行は Nablarch 5 の最新版へ上げた後に実施してください

参照: migration-migration.json:s2, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29