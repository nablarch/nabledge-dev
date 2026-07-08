**結論**: Nablarch 5からNablarch 6へのバージョンアップでJakarta EE 10対応に伴うアプリケーションへの主な影響は、(1) `javax.*` 名前空間を `jakarta.*` へ変更、(2) Java EE API依存関係をJakarta EE版に差し替え、(3) XMLスキーマ・JSPタグライブラリのネームスペース変更、(4) 開発・テスト用プラグインの切り替えです。

**根拠**:

移行手順は大きく「Nablarchのバージョンアップ」と「Jakarta EE対応」の2つに分かれます。

---

**① Nablarch BOMのバージョン変更**

`pom.xml` で参照するNablarchのBOMバージョンを変更します。

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.nablarch.profile</groupId>
      <artifactId>nablarch-bom</artifactId>
      <version>6u2</version>  <!-- 5u25 などから変更 -->
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

---

**② Java EE API依存関係をJakarta EE版へ変更**

Jakarta EE BOMを読み込むと個別バージョン管理が不要になります。

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

代表的な変更例：

| Java EE | Jakarta EE |
|--------|-----------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| `org.apache.activemq:activemq-all` (JMS) | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` (各 2.37.0) |
| Jersey BOM (古いバージョン) | Jersey BOM `3.1.8` |

---

**③ `javax` 名前空間を `jakarta` 名前空間に変更**

Javaソースコード・JSP・設定ファイル内の `javax.` をプロジェクト全体でGrep検索し、Java EEの名前空間であるものを `jakarta.` に変更します。

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

注意: `javax.crypto.*` など標準ライブラリの名前空間は変更不要です。

---

**④ XMLスキーマをJakarta EE 10版に変更**

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

---

**⑤ JSPのタグライブラリネームスペース変更**

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

**⑥ 開発用サーバの変更（Webプロジェクトのみ）**

`waitt-maven-plugin` はJakarta EE未対応のため `jetty-ee10-maven-plugin` に変更します。

```xml
<!-- 修正後 -->
<plugin>
  <groupId>org.eclipse.jetty.ee10</groupId>
  <artifactId>jetty-ee10-maven-plugin</artifactId>
  <version>12.0.12</version>
</plugin>
```

---

**⑦ テスト用組み込みサーバの変更（Webプロジェクトのみ）**

`pom.xml`:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-testing-jetty12</artifactId>  <!-- jetty6/jetty9 から変更 -->
  <scope>test</scope>
</dependency>
```

`unit-test.xml`:
```xml
<!-- 修正後 -->
<component name="httpServerFactory" class="nablarch.fw.web.httpserver.HttpServerFactoryJetty12"/>
```

---

**⑧ Jakarta Batchアプリケーション向けJBeret依存関係更新**

`javax.batch` 等を `jakarta.batch` 等に変更し、JBeret関連ライブラリのバージョンも更新します（例: `jberet-core:2.1.4.Final`、`weld-core-impl:5.0.1.Final`）。詳細は移行ガイド参照。

---

**⑨ gsp-dba-maven-pluginの更新（使用している場合）**

Jakarta EEおよびNablarch 6u2対応のバージョン 5.1.0 に変更します。

```xml
<plugin>
  <groupId>jp.co.tis.gsp</groupId>
  <artifactId>gsp-dba-maven-plugin</artifactId>
  <version>5.1.0</version>
```

---

**注意点**:
- アプリケーションサーバ自体もJakarta EE 10に対応したものが必要です
- Nablarchが提供するクラスやパッケージ名は後方互換のために変更されていませんが、一部Nablarch機能の名称がJakarta EE準拠に変更されています（例: 「JAX-RSアダプタ」→「Jakarta RESTful Web Servicesアダプタ」）
- `javax.crypto.*` などのJava標準ライブラリはJava EEの名前空間ではないため変更不要です

参照:
- Nablarch 5から6への移行ガイド
  .claude/skills/nabledge-6/docs/about/migration/migration-migration.md
  Jakarta EE 10に対応
  移行手順の概要
  Nablarchのバージョンアップ
  Java EEの依存関係をJakarta EEに変更する
  Java EE仕様の実装ライブラリを更新する
  javax名前空間をjakarta名前空間に変更する
  XMLスキーマ指定をJakarta EE 10のスキーマに変更する
  タグライブラリのネームスペースをJakarta EE 10のネームスペースに変更する
  waitt-maven-pluginをjetty-ee10-maven-pluginに変更する
  nablarch-testing-jetty6をnablarch-testing-jetty12に変更する
  JSR352に準拠したバッチアプリケーションの移行手順
  gsp-dba-maven-pluginを更新する