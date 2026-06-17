**結論**: Jakarta EE 10対応では「名前空間の`javax.*`→`jakarta.*`変更」を中心に、依存ライブラリの更新・XMLスキーマ変更・ツール類の置き換えなど、アプリケーション全体にわたる修正が必要です。後方互換性は維持されません。

---

**根拠**:

## 1. 名前空間の変更（全プロジェクト共通・最重要）

Jakarta EE 9でパッケージ名が `javax.*` から `jakarta.*` に変更されました。Javaコード・JSP・設定ファイルのすべてが対象です。

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

注意: `javax.crypto.SecretKeyFactory` のような Java標準ライブラリの `javax.*` は対象外です。プロジェクト全体をGrepして Java EEの名前空間か否かを判断する必要があります。

---

## 2. Java EE API依存関係をJakarta EEへ変更

`pom.xml` のdependencyをJakarta EE版に差し替えます。Jakarta EE BOMを導入してバージョン管理を一元化することを推奨します。

```xml
<!-- BOM追加（推奨） -->
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

主な変更例:

| Java EE (修正前) | Jakarta EE (修正後) |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `jakarta.ws.rs`へ変更 | `javax.ws.rs:javax.ws.rs-api` → `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |
| `javax.persistence` (JPA) | `jakarta.persistence:jakarta.persistence-api` |

---

## 3. Java EE実装ライブラリの更新

主な変更:

**Bean Validation（hibernate-validator）**:
```xml
<!-- 修正前 -->
<dependency>
  <groupId>org.hibernate</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>5.3.6.Final</version>
</dependency>

<!-- 修正後 -->
<dependency>
  <groupId>org.hibernate.validator</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>8.0.0.Final</version>
</dependency>
```

**JSTL実装**:
```xml
<!-- 修正後 -->
<dependency>
  <groupId>org.glassfish.web</groupId>
  <artifactId>jakarta.servlet.jsp.jstl</artifactId>
  <version>3.0.0</version>
</dependency>
```

**JAX-RS実装（Jersey）**: jersey-bomのバージョンを3.1.8以降に変更。

**JMS実装（ActiveMQ）**: `activemq-all` → `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client`。

---

## 4. XMLスキーマ変更（web.xml等）

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

---

## 5. JSPのタグライブラリネームスペース変更

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

## 6. ツール類の更新

| 修正前 | 修正後 | 対象 |
|---|---|---|
| `waitt-maven-plugin` | `jetty-ee10-maven-plugin 12.0.12` | ウェブプロジェクトの組み込みサーバ起動 |
| `nablarch-testing-jetty6`（または jetty9） | `nablarch-testing-jetty12` + `HttpServerFactoryJetty12` | NTFのテスト用組み込みサーバ |
| `gsp-dba-maven-plugin` | バージョン 5.1.0（Jakarta EE対応版） | エンティティクラス生成 |

---

## 7. Domaアダプタ・Micrometerアダプタの更新

- **Domaアダプタ**: 依存関係の設定変更と推奨実装方法への移行が必要
- **Micrometerアダプタ**: 監視サービス連携ライブラリのバージョン更新が必要

---

## 8. Jakarta Batch（JBeret）のみ追加の移行手順

JBeretとその関連ライブラリ（weld-core等）をJakarta EE対応版へ全面的に置き換えます。`javax.el:glassfish` → `expressly 5.0.0`、`jberet-core` → 2.1.4.Final など多数の依存関係変更が必要です。

---

**注意点**:
- 名前空間変更により後方互換性は一切維持されません。Jakarta EE 10対応のアプリケーションサーバ（Tomcat 10以降等）が必要です
- 動作にはJava 17以上が必要です
- 移行手順はNablarch 5の最新版（5u25相当）からNablarch 6u2へのアップグレードを前提としています。6u3以降へのバージョンアップには追加手順が必要なため、各リリースノートを確認してください

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s20, migration-migration.json:s21, migration-migration.json:s22, migration-migration.json:s23, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29, about-nablarch-jakarta-ee.json:s2