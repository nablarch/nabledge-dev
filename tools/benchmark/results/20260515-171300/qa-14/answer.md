**結論**: Nablarch 5からNablarch 6へのバージョンアップにあたり、Jakarta EE 10対応としてアプリケーションに影響する変更は大きく分けて「依存関係の変更」「ソースコードの名前空間変更」「設定ファイルの変更」の3カテゴリに分類されます。

**根拠**:

### 1. Nablarchのバージョンアップ

`pom.xml` のBOMバージョンを `6u2` に変更します。

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

### 2. Java EEの依存関係をJakarta EEに変更する

`groupId` / `artifactId` を以下の通り変更します（Jakarta EE BOMの読み込みを推奨）。

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

### 3. Java EE仕様の実装ライブラリを更新する

| ライブラリ | 変更内容 |
|-----------|---------|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` → `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL実装 | `taglibs:standard` → `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS実装 (Jersey) | jersey-bom のバージョンを `3.1.8` に更新 |
| JMS (ActiveMQ) | `activemq-all` → `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` |

### 4. 関連ツール・プラグインの更新（ウェブプロジェクト）

| ツール | 変更内容 |
|--------|---------|
| `waitt-maven-plugin` | Jakarta EE非対応のため `jetty-ee10-maven-plugin:12.0.12` に変更 |
| `nablarch-testing-jetty6` | Jetty 6はJakarta EE非対応のため `nablarch-testing-jetty12` に変更し、`HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` に変更 |
| `gsp-dba-maven-plugin` | `5.1.0` に更新（Jakarta EE対応版） |

### 5. ソースコードの名前空間変更

Jakarta EE 9で `javax.*` から `jakarta.*` に名前空間が変更されました。対応手順は以下のとおりです。

1. `javax` でImportしている箇所はコンパイルエラーになるため `jakarta` に変更
2. プロジェクト全体を `javax` でGrepして漏れを確認
3. Java EEの名前空間か（`javax.crypto` などの標準ライブラリと区別）を確認
4. Java EEの名前空間であれば `javax` → `jakarta` に置換

例:
```java
// 変更前
import javax.validation.ConstraintValidator;
// 変更後
import jakarta.validation.ConstraintValidator;
```

文字列リテラルも対象です（例: `"javax.servlet.forward.request_uri"` → `"jakarta.servlet.forward.request_uri"`）。

### 6. XMLスキーマ指定の変更

`web.xml` 等のXMLファイルのスキーマを更新します。

```xml
<!-- 変更前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

### 7. JSPのタグライブラリネームスペース変更

```jsp
<%-- 変更前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 変更後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 8. JSR352バッチアプリケーションの依存関係変更（Jakarta Batch使用時のみ）

JBeretおよび関連ライブラリ（CDI、JTA等）を全てJakarta EE対応版に更新する必要があります（`jberet-core:2.1.4.Final`、`weld-core-impl:5.0.1.Final` 等）。

**注意点**:
- 上記移行手順は Nablarch 5の**最新版**へのバージョンアップが完了していることが前提です。古いバージョンからの直接移行はサポートされていません
- Java 17以上および Jakarta EE 10対応のアプリケーションサーバが必要です（後方互換性なし）
- `javax` で検索したとき `javax.crypto` など**Java標準ライブラリ**のクラスはJakarta EEとは無関係であり、変更不要です
- 6u3以降へバージョンアップする場合は、各リリースノートを順に確認して追加手順がないか必ず確認してください

参照: `about/migration/migration-migration.json#s2`, `#s5`, `#s9`, `#s16`, `#s26`, `#s27`, `#s28`