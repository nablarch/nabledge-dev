**結論**: Nablarch 5→6移行でJakarta EE 10対応として必要な変更は、①Nablarchバージョンアップ、②Java EE依存関係をJakarta EEに置き換え、③`javax`名前空間を`jakarta`に変更、④XMLスキーマ・タグライブラリのネームスペース更新、の4つです。Java 17以上のJavaおよびJakarta EE 10対応アプリサーバが必要です。

**根拠**:

**① Nablarchのバージョンアップ**

`pom.xml` のBOMバージョンを変更します。

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**② Java EE依存関係 → Jakarta EE依存関係への変更**

主な変更例：

| 変更前 | 変更後 |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

実装ライブラリも更新が必要です：

- **Bean Validation**: `org.hibernate:hibernate-validator:5.x` → `org.hibernate.validator:hibernate-validator:8.0.0.Final`
- **JSTL実装**: `taglibs:standard` → `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0`
- **JAX-RS (Jersey)**: jersey-bom → `3.1.8` 以上
- **JMS (ActiveMQ)**: `activemq-all` → `artemis-jakarta-server` / `artemis-jakarta-client`

**③ `javax`名前空間を`jakarta`名前空間に変更する**

Javaソースコードでコンパイルエラーになる箇所に加え、プロジェクト全体をGrepして `javax` を検索し、Java EEの名前空間に該当するものを `jakarta` に置換します。

```java
// 変更前
import javax.validation.ConstraintValidator;

// 変更後
import jakarta.validation.ConstraintValidator;
```

> **注意**: `javax.crypto` など標準ライブラリの `javax` はJava EEではないので変更不要です。

**④ XMLスキーマ・タグライブラリのネームスペース変更**

`web.xml` のXMLスキーマ:

```xml
<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee web-app_6_0.xsd"
         version="6.0">
```

JSPのtaglibディレクティブ:

```jsp
<%-- 変更後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

**ウェブアプリ固有の追加変更**

- テスト用組み込みサーバを変更: `nablarch-testing-jetty6` → `nablarch-testing-jetty12`
- コンポーネント定義: `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12`
- 開発用サーバ: `waitt-maven-plugin` → `jetty-ee10-maven-plugin:12.0.12`

**Jakarta Batchアプリ固有の追加変更**

JBeret関連の依存関係を全てJakarta EE対応版に更新します（`jberet-core:2.1.4.Final`、`weld-core-impl:5.0.1.Final`、`jakarta.batch:jakarta.batch-api` など）。

**注意点**:
- Java 17以上が必須（Nablarch 6のモジュールはJava 17でコンパイルされているため）
- Jakarta EE 10対応アプリサーバ（例: Tomcat 10）が必要
- gsp-dba-maven-pluginを使用している場合は `5.1.0` へのアップデートが必要

参照:
- Nablarch 5から6への移行ガイド
  .claude/skills/nabledge-6/docs/about/migration/migration-migration.md
  Jakarta EE 10に対応
  動作に必要なJavaの最低バージョンを17に変更
  移行手順の概要
  Nablarchのバージョンアップ
  Java EEの依存関係をJakarta EEに変更する
  Java EE仕様の実装ライブラリを更新する
  waitt-maven-pluginをjetty-ee10-maven-pluginに変更する
  nablarch-testing-jetty6をnablarch-testing-jetty12に変更する
  javax名前空間をjakarta名前空間に変更する
  XMLスキーマ指定をJakarta EE 10のスキーマに変更する
  タグライブラリのネームスペースをJakarta EE 10のネームスペースに変更する
  JSR352に準拠したバッチアプリケーションの移行手順