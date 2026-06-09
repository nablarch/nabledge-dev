**結論**: Nablarch 5→6のJakarta EE 10対応では、名前空間の `javax.*` → `jakarta.*` への一斉変更、依存関係のJakarta EE版への置き換え、および関連ファイルの更新が必要です。後方互換性は維持されないため、Jakarta EE 10対応のアプリケーションサーバへの切り替えも必須です。

**根拠**:

### 1. 前提条件の変更
- **Java 17以上**が必要（Nablarch 6のモジュールはJava 17でコンパイル）
- **Jakarta EE 10対応のアプリケーションサーバ**が必要（Tomcat 10.x等）

### 2. pom.xml: NablarchのBOM更新

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>  <!-- 5→6u2 に変更 -->
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

Jakarta EE BOMの追加も推奨:
```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

### 3. Java EE API依存関係 → Jakarta EE版に変更

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

### 4. Java EE実装ライブラリの更新

| 変更前 | 変更後 |
|--------|--------|
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| `jersey-bom` (旧バージョン) | `jersey-bom:3.1.8` |
| `org.apache.activemq:activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` |

### 5. Javaコード: javax名前空間をjakarta名前空間に変更

```java
// 変更前
import javax.validation.ConstraintValidator;

// 変更後
import jakarta.validation.ConstraintValidator;
```

コンパイルエラーにならない箇所（文字列定数、JSP、設定ファイル）も含め、プロジェクト全体を `javax` でGrep検索して修正が必要。ただし `javax.crypto` 等のJava標準ライブラリはJava EEの名前空間ではないため変更不要。

### 6. web.xml等のXMLスキーマ変更

```xml
<!-- 変更前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         version="3.1">

<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee web-app_6_0.xsd"
         version="6.0">
```

### 7. JSP: タグライブラリのネームスペース変更

```jsp
<!-- 変更前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 変更後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 8. ウェブアプリ固有の変更

- **waitt-maven-plugin** → **jetty-ee10-maven-plugin:12.0.12**（開発時サーバ実行）
- **nablarch-testing-jetty6** → **nablarch-testing-jetty12**（NTFテスト用組み込みサーバ）
  - コンポーネント定義: `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12`

### 9. Jakarta Batch（JBeret）固有の大規模依存関係変更

`javax.batch`、`javax.inject`、`javax.enterprise` 等の依存関係を全面的にJakarta EE版に変更（`jakarta.batch-api`、`jakarta.inject-api`、`jakarta.enterprise.cdi-api` 等）、JBeret 2.1.4.Final、Weld 5.0.1.Final 等に更新が必要。

### 10. 機能名の変更（名称のみ、機能変更なし）

| Nablarch 5の名称 | Nablarch 6の名称 |
|-----------------|----------------|
| JAX-RSアダプタ | Jakarta RESTful Web Servicesアダプタ |
| JAX-RSレスポンスハンドラ | Jakarta RESTful Web Servicesレスポンスハンドラ |
| JSPカスタムタグ | Jakarta Server Pagesカスタムタグ |
| JSR352に準拠したバッチ | Jakarta Batchに準拠したバッチ |

**注意点**: `javax` を検索した際、`javax.crypto` や `javax.sql` 等のJava標準ライブラリはJava EEの名前空間ではないため変更不要。Java EEの名前空間かどうかは、移行ガイド付録の「Java EEとJakarta EEの仕様の対応表」で確認すること。

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29, about-nablarch-jakarta-ee.json:s2