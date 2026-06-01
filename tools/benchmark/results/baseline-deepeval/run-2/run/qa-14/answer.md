**結論**: Nablarch 5からNablarch 6へのJakarta EE 10対応では、アプリケーション側で「名前空間の変更（`javax.*` → `jakarta.*`）」「依存ライブラリの置き換え」「設定ファイルの更新」の3種類の変更が必要です。

---

**根拠**:

## 1. Nablarchのバージョンアップ（BOM変更）

`pom.xml` の NablarchBOM バージョンを変更します：

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>  <!-- 5.x.x から変更 -->
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

---

## 2. Java EE依存関係をJakarta EEに変更

Jakarta EE BOMの導入を推奨します：

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

主な依存関係の変更例：

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

---

## 3. 実装ライブラリの更新

**Bean Validation（Hibernate Validator）**：

```xml
<!-- 変更前 -->
<dependency>
  <groupId>org.hibernate</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>5.3.6.Final</version>
</dependency>

<!-- 変更後 -->
<dependency>
  <groupId>org.hibernate.validator</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>8.0.0.Final</version>
</dependency>
```

**JAX-RS（Jersey）**： Jersey BOMのバージョンを `3.1.8` に変更します。

**JMS（ActiveMQ）**：

```xml
<!-- 変更後（artemis-serverとjakarta対応モジュールに変更） -->
<dependency>
  <groupId>org.apache.activemq</groupId>
  <artifactId>artemis-server</artifactId>
  <version>2.37.0</version>
</dependency>
<dependency>
  <groupId>org.apache.activemq</groupId>
  <artifactId>artemis-jakarta-server</artifactId>
  <version>2.37.0</version>
</dependency>
<dependency>
  <groupId>org.apache.activemq</groupId>
  <artifactId>artemis-jakarta-client</artifactId>
  <version>2.37.0</version>
</dependency>
```

---

## 4. ソースコード・設定ファイルの名前空間変更

プロジェクト全体を `javax` でGrep検索し、Java EE名前空間をすべて `jakarta` に置換します：

```java
// 変更前
import javax.validation.ConstraintValidator;
// 変更後
import jakarta.validation.ConstraintValidator;
```

**注意点**: `javax.crypto.SecretKeyFactory` のようなJava標準ライブラリの `javax.*` は変更不要です。

---

## 5. web.xmlのXMLスキーマ変更

```xml
<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

---

## 6. JSPタグライブラリのネームスペース変更

```jsp
<%-- 変更前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 変更後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

## 7. ウェブ開発ツールの変更（Webプロジェクトのみ）

- `waitt-maven-plugin` → `jetty-ee10-maven-plugin`（バージョン `12.0.12`）
- `nablarch-testing-jetty6` → `nablarch-testing-jetty12`（テストの組み込みサーバ）
- `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12`（unit-test.xml設定）

---

## 8. Jakarta Batch専用の依存関係更新

JSR352（Jakarta Batch）プロジェクトでは、JBeret関連ライブラリを全面的に更新します（例：`jberet-core` を `2.1.4.Final`、`weld-core-impl` を `5.0.1.Final` 等）。

---

**注意点**:
- 移行手順は Nablarch 5 最新版（5u25相当）から **6u2** へのバージョンアップを前提としています。6u3以降へのバージョンアップは各リリースノートも順に確認が必要です。
- アプリケーションサーバ自体もJakarta EE 10対応版（Tomcat 10以降等）への更新が必要です。
- gsp-dba-maven-pluginを使用している場合はバージョン `5.1.0` に更新が必要です。

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s10, migration-migration.json:s11, migration-migration.json:s12, migration-migration.json:s13, migration-migration.json:s14, migration-migration.json:s15, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s20, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29, releases-nablarch6-releasenote-6.json:s2, releases-nablarch6-releasenote-6.json:s3