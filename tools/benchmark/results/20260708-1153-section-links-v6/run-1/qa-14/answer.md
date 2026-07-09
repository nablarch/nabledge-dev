**結論**: Nablarch 5→6のJakarta EE 10対応で、アプリケーションに影響する変更は主に「①`javax.*`名前空間を`jakarta.*`に変更」「②Java EE依存関係をJakarta EE版に変更」「③実装ライブラリの更新」「④XMLスキーマ・JSPタグライブラリのネームスペース変更」の4カテゴリです。Jakarta Batchを使用する場合はJBeret関連ライブラリの更新も必要です。

---

**根拠**:

#### ① `javax` 名前空間を `jakarta` 名前空間に変更する

Jakarta EE 9 で最大の変更として名前空間が `javax.*` から `jakarta.*` に変更されました。Javaソースコード・JSP・設定ファイルのすべてが対象です。

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

コンパイルエラーで検出できない箇所（文字列として埋め込まれたキーなど）も存在するため、プロジェクト全体を `javax` でGrep検索して確認が必要です。

主なJava EE→Jakarta EEの名前空間対応:

| Java EE 仕様 | 旧名前空間 | Jakarta EE 仕様 |
|---|---|---|
| Java Servlet | `javax.servlet` | Jakarta Servlet |
| Bean Validation | `javax.validation` | Jakarta Bean Validation |
| JPA | `javax.persistence` | Jakarta Persistence |
| JAX-RS | `javax.ws.rs` | Jakarta RESTful Web Services |
| JMS | `javax.jms` | Jakarta Messaging |

---

#### ② Java EE API の依存関係を Jakarta EE 版に変更する

`pom.xml` 上の Java EE API の `dependency` を Jakarta EE のものに変更します。Jakarta EE の BOM を使用することを推奨します。

```xml
<!-- Jakarta EE BOMを読み込む（推奨） -->
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

代表的な変更例:

```xml
<!-- Java Servlet -->
<!-- 修正前 -->
<dependency>
  <groupId>javax.servlet</groupId>
  <artifactId>javax.servlet-api</artifactId>
</dependency>
<!-- 修正後 -->
<dependency>
  <groupId>jakarta.servlet</groupId>
  <artifactId>jakarta.servlet-api</artifactId>
</dependency>
```

```xml
<!-- JPA -->
<!-- 修正前 -->
<dependency>
  <groupId>org.apache.geronimo.specs</groupId>
  <artifactId>geronimo-jpa_2.0_spec</artifactId>
</dependency>
<!-- 修正後 -->
<dependency>
  <groupId>jakarta.persistence</groupId>
  <artifactId>jakarta.persistence-api</artifactId>
</dependency>
```

---

#### ③ Java EE 仕様の実装ライブラリを更新する

| 仕様 | 修正前 | 修正後 |
|---|---|---|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL | `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS (Jersey) | jersey-bom（旧バージョン） | `org.glassfish.jersey:jersey-bom:3.1.8` |
| JMS (ActiveMQ) | `activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` (2.37.0) |

---

#### ④ XMLスキーマとタグライブラリのネームスペースを変更する

`web.xml` などのXMLスキーマ宣言を Jakarta EE 10 用に変更します。

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

JSPの `taglib` ディレクティブも変更が必要です。

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

#### ⑤ Jakarta Batch (JSR352) を使用している場合の追加対応

JBeret と関連ライブラリを Jakarta EE 対応版に更新します。

```xml
<!-- 修正後の主な依存関係 -->
<dependency>
  <groupId>jakarta.batch</groupId>
  <artifactId>jakarta.batch-api</artifactId>
</dependency>
<dependency>
  <groupId>org.jberet</groupId>
  <artifactId>jberet-core</artifactId>
  <version>2.1.4.Final</version>
</dependency>
<dependency>
  <groupId>org.jboss.weld</groupId>
  <artifactId>weld-core-impl</artifactId>
  <version>5.0.1.Final</version>
</dependency>
```

---

**注意点**:
- 開発用組み込みサーバも変更が必要です: `waitt-maven-plugin` → `jetty-ee10-maven-plugin:12.x`、`nablarch-testing-jetty6` → `nablarch-testing-jetty12`（テストの `HttpServerFactory` の設定も `HttpServerFactoryJetty12` に変更）。
- Jakarta Batch で `NoClassDefFoundError` が発生する場合は、`pom.xml` 上で `slf4j-nablarch-adaptor` の記述位置を Logback より後に移動することで解消できます。
- 移行対象は Nablarch 5 の最新版からの移行を前提としています。古いバージョンの場合は先に Nablarch 5 の最新版へのバージョンアップが必要です。

参照:
- Nablarch 5から6への移行ガイド
  .claude/skills/nabledge-6/docs/about/migration/migration-migration.md
  Jakarta EE 10に対応
  動作に必要なJavaの最低バージョンを17に変更
  移行手順の概要
  Java EEの依存関係をJakarta EEに変更する
  Java EE仕様の実装ライブラリを更新する
  javax名前空間をjakarta名前空間に変更する
  XMLスキーマ指定をJakarta EE 10のスキーマに変更する
  タグライブラリのネームスペースをJakarta EE 10のネームスペースに変更する
  JSR352に準拠したバッチアプリケーションの移行手順
- ■Nablarch 6 リリースノート
  .claude/skills/nabledge-6/docs/releases/releases/releases-nablarch6-releasenote-6.md
  Jakarta EE 10対応
  必要Javaバージョンの変更