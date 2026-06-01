**結論**: Nablarch 5→6へのバージョンアップでJakarta EE 10対応を行うには、①Javaおよびアプリケーションサーバの環境変更、②pom.xml上の依存関係変更（Java EE → Jakarta EE）、③Javaソースコード・設定ファイル内の `javax.*` → `jakarta.*` 名前空間置換、の3つが必要です。

---

**根拠**:

## 1. 環境の変更（必須）

- **Java 17以上が必要**: Nablarch 6のモジュールはJava 17でコンパイルされているため
- **Jakarta EE 10対応アプリケーションサーバが必要**: Nablarch 5のアプリはJava EEのASで動いていたが、Nablarch 6はJakarta EE 10対応ASが必須

## 2. pom.xml の変更

### 2-1. Nablarch BOMのバージョンアップ

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>  <!-- 5u25 → 6u2 -->
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

### 2-2. Jakarta EE BOMの追加（推奨）

バージョン管理を楽にするため、Jakarta EEのBOMの追加を推奨：

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

### 2-3. Java EE API依存関係 → Jakarta EE API依存関係への変更（代表例）

| 仕様 | 修正前 | 修正後 |
|------|--------|--------|
| Java Servlet | `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| JSP | `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| JSTL (API) | `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| JPA | `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| JAX-RS | `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| Jakarta Annotations | `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

### 2-4. Java EE仕様の実装ライブラリの変更（代表例）

```xml
<!-- Bean Validation (hibernate-validator) -->
<!-- 修正前 -->
<groupId>org.hibernate</groupId>
<artifactId>hibernate-validator</artifactId>
<version>5.3.6.Final</version>
<!-- 修正後 -->
<groupId>org.hibernate.validator</groupId>
<artifactId>hibernate-validator</artifactId>
<version>8.0.0.Final</version>
```

```xml
<!-- JSTL実装 -->
<!-- 修正前: taglibs:standard -->
<!-- 修正後 -->
<groupId>org.glassfish.web</groupId>
<artifactId>jakarta.servlet.jsp.jstl</artifactId>
<version>3.0.0</version>
```

```xml
<!-- JAX-RS実装 (Jersey) -->
<!-- jersey-bom バージョンを 3.1.8 に変更 -->
<groupId>org.glassfish.jersey</groupId>
<artifactId>jersey-bom</artifactId>
<version>3.1.8</version>
```

```xml
<!-- JMS実装 (ActiveMQ) -->
<!-- 修正前: org.apache.activemq:activemq-all -->
<!-- 修正後: artemis-server + artemis-jakarta-server + artemis-jakarta-client (各2.37.0) -->
```

### 2-5. 開発ツール・プラグインの変更

| ツール | 変更内容 |
|--------|---------|
| `waitt-maven-plugin` | `jetty-ee10-maven-plugin 12.0.12` に変更（Webプロジェクト） |
| `nablarch-testing-jetty6` | `nablarch-testing-jetty12` に変更。`HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` |
| `gsp-dba-maven-plugin` | `5.1.0` に更新（Jakarta EE対応版） |
| Domaアダプタ | 依存関係の設定変更が必要（アダプタの解説書参照） |

### 2-6. Jakarta Batchアプリケーション（JSR352）の場合

JBeretおよび関連ライブラリを全てJakarta EE対応版に変更する必要あり（変更内容は複数のライブラリに及ぶため詳細は移行ガイド参照）：

```xml
<!-- 例: jberet-core -->
<groupId>org.jberet</groupId>
<artifactId>jberet-core</artifactId>
<version>2.1.4.Final</version>  <!-- Jakarta EE対応版 -->
```

## 3. ソースコード・設定ファイルの修正

### 3-1. `javax.*` → `jakarta.*` 名前空間の置換

**対象範囲**:
- Javaソースコードの `import` 文（コンパイルエラーとして検出可能）
- 文字列リテラル（例: `"javax.servlet.forward.request_uri"` → `"jakarta.servlet.forward.request_uri"`）
- JSPファイル内の記述
- 設定ファイル内の記述

**注意**: `javax.crypto.*` などJava標準ライブラリの名前空間は変更不要。付録の「Java EEとJakarta EEの仕様の対応表」を参照して判断すること。

```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

### 3-2. `web.xml` のXMLスキーマ変更

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

### 3-3. JSPのtaglibネームスペース変更

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

**注意点**:
- 移行前に必ずNablarch 5の最新版（5u25）へのバージョンアップを完了させること
- `javax` でプロジェクト全体をGrep検索し、Java EEの名前空間かどうかを1件ずつ判断する必要がある（機械的に一括置換はできない）
- Nablarchが提供するクラス・パッケージ名自体は後方互換維持のため変更されていないため、Nablarch固有クラスの `import` は変更不要

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s10, migration-migration.json:s11, migration-migration.json:s12, migration-migration.json:s13, migration-migration.json:s14, migration-migration.json:s15, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s20, migration-migration.json:s21, migration-migration.json:s23, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29, about-nablarch-jakarta-ee.json:s2

---