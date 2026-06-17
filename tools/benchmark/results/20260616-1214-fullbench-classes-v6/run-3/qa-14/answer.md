**結論**: Nablarch 5 → 6 のJakarta EE 10対応では、主に「依存関係の置き換え」「名前空間の変更（`javax.*` → `jakarta.*`）」「設定ファイルのスキーマ更新」の3系統の変更が必要です。

---

**根拠**:

#### 1. 動作環境の変更（必須）

- **Java 17以上が必要**: Nablarch 6モジュールはJava 17でコンパイルされている
- **Jakarta EE 10対応のアプリケーションサーバが必要**: 名前空間変更などにより後方互換性が維持されない

#### 2. pom.xml: NablarchのBOMバージョン変更

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>   <!-- 5u** → 6u2 -->
  ...
</dependency>
```

#### 3. pom.xml: Java EE APIの依存関係をJakarta EEに変更

主な変更例：

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

Jakarta EE BOMをまとめて読み込む方法を推奨：
```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

#### 4. pom.xml: 実装ライブラリのバージョン更新

| ライブラリ | 変更内容 |
|-----------|---------|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` → `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL | `taglibs:standard` → `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS (Jersey) | `jersey-bom` のバージョンを3.1.8に更新 |
| JMS (ActiveMQ) | `activemq-all` → `artemis-server` / `artemis-jakarta-server` / `artemis-jakarta-client` |

#### 5. Javaソースコード・設定ファイル: javax名前空間をjakartaに変更

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

コンパイルエラーにならないケース（文字列指定）も存在するため、プロジェクト全体を `javax` でGrep検索して漏れなく対応する必要がある。

#### 6. web.xml等: XMLスキーマをJakarta EE 10に変更

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

#### 7. JSP: タグライブラリのネームスペースを変更

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

#### 8. テスト環境: Jettyモジュールの変更（ウェブアプリのみ）

```xml
<!-- 修正前 -->
<artifactId>nablarch-testing-jetty6</artifactId>

<!-- 修正後 -->
<artifactId>nablarch-testing-jetty12</artifactId>
```

合わせて `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` に変更する。

#### 9. Jakarta Batch（JBeret）を使っている場合の追加対応

JBeretと関連ライブラリの置き換えが必要（javax系→jakarta系への変更が複雑）。例：
- `org.jboss.spec.javax.batch:jboss-batch-api_1.0_spec` → `jakarta.batch:jakarta.batch-api`
- `javax.inject:javax.inject` → `jakarta.inject:jakarta.inject-api`
- `org.jboss.weld:weld-core` → `org.jboss.weld:weld-core-impl:5.0.1.Final`

**注意点**:
- `javax.crypto.SecretKeyFactory` など標準ライブラリの `javax` 名前空間はJava EEではないため変更不要
- waitt-maven-plugin（ウェブアプリのみ）は jetty-ee10-maven-plugin へ置き換えが必要
- gsp-dba-maven-plugin を使っている場合は5.1.0へ更新が必要

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s20, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29