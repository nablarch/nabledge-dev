**結論**: Nablarch 5→6のJakarta EE 10対応では、「名前空間 `javax.*` → `jakarta.*` への変更」「Java EEのAPI依存関係をJakarta EE版に変更」「実装ライブラリ・ツールの更新」の3つの大きな対応が必要です。後方互換性は維持されないため、アプリケーションサーバもJakarta EE 10対応版に切り替える必要があります。

**根拠**:

**① API依存関係の変更 (pom.xml)**

Java EEのAPI依存関係をJakarta EEのものに変更します。代表例：

| 変更前 | 変更後 |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

版数管理の簡略化のため、Jakarta EE BOMの読み込みを推奨します：

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**② 実装ライブラリの更新**

| 変更前 | 変更後 |
|---|---|
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| Jersey BOM (旧バージョン) | `org.glassfish.jersey:jersey-bom:3.1.8` |
| `org.apache.activemq:activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` |

**③ javax名前空間をjakarta名前空間に変更**

Jakarta EE 9で `javax.*` → `jakarta.*` の名前空間変更が入りました。対応手順：

1. `javax` でGrep検索し、Java EE名前空間である箇所を特定する
2. 該当箇所を `jakarta` に置換する

例：
```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

※ `javax.crypto.SecretKeyFactory` のような標準ライブラリは変更不要（Java EE名前空間ではない）

**④ XMLスキーマの変更 (web.xmlなど)**

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">
<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

**⑤ JSPタグライブラリのネームスペース変更**

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

**⑥ ツール・プラグインの更新**

| ツール | 変更内容 |
|---|---|
| `waitt-maven-plugin` | `jetty-ee10-maven-plugin:12.0.12` に変更（Jakarta EE非対応のため） |
| `nablarch-testing-jetty6` | `nablarch-testing-jetty12` に変更し、`HttpServerFactoryJetty12` クラスを使用 |
| `gsp-dba-maven-plugin` | `5.1.0` に更新（Jakarta EE対応版） |

**⑦ Nablarchの機能名称変更**

機能の変更はなく名称のみ変更（クラス・パッケージ名は後方互換維持）：

| Nablarch5 | Nablarch6 |
|---|---|
| JAX-RSアダプタ | Jakarta RESTful Web Servicesアダプタ |
| JSPカスタムタグ | Jakarta Server Pagesカスタムタグ |
| JSR352に準拠したバッチアプリケーション | Jakarta Batchに準拠したバッチアプリケーション |

**⑧ Jakarta Batchアプリケーション固有の追加手順**

JBeretと関連ライブラリの更新が必要です（`jakarta.batch:jakarta.batch-api`、`org.jberet:jberet-core:2.1.4.Final`、`weld-core-impl:5.0.1.Final` 等への変更）。

**注意点**:
- 移行手順はNablarch 5の最新版（5u25相当）からNablarch 6u2へのバージョンアップを前提としています
- 6u3以降にバージョンアップする場合は、各バージョンのリリースノートも確認が必要です
- アプリケーションサーバ自体もJakarta EE 10対応版への切り替えが必要です（名前空間変更により後方互換なし）

参照: about/migration/migration-migration.json:s2, about/migration/migration-migration.json:s5, about/migration/migration-migration.json:s9, about/migration/migration-migration.json:s16, about/migration/migration-migration.json:s26, about/migration/migration-migration.json:s27, about/migration/migration-migration.json:s28, about/about-nablarch/about-nablarch-jakarta-ee.json:s2