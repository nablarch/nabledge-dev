**結論**: Nablarch 5からNablarch 6へ移行する際、Jakarta EE 10対応として主に「依存関係の変更」「名前空間（`javax` → `jakarta`）の置換」「XMLスキーマ・タグライブラリのネームスペース変更」「関連ツール・プラグインの更新」が必要です。

**根拠**:

### 1. 名前空間の変更（最も広範な影響）

Jakarta EE 9でパッケージ名前空間が `javax.*` から `jakarta.*` に変更されました。アプリケーションコード全体に影響します。

対応手順:
1. `javax` でプロジェクト全体をGrep検索
2. Java EEの名前空間かどうか判定（例: `javax.crypto.*` はJava標準ライブラリのため変更不要）
3. Java EEの名前空間であれば `javax` → `jakarta` に置換

```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

コンパイルエラーにならない箇所（文字列リテラル、JSP、設定ファイル）にも `javax` が残る場合があります。例: `javax.servlet.forward.request_uri` → `jakarta.servlet.forward.request_uri`

### 2. Maven依存関係の変更

Java EEのAPI依存関係をJakarta EE版に変更します。Jakarta EE BOMの導入を推奨:

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

主な変更例:

| 変更前 | 変更後 |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

### 3. 実装ライブラリの更新

| ライブラリ | 変更内容 |
|---|---|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` → `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL実装 | `taglibs:standard` → `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS (Jersey) | jersey-bom を `3.1.8` に更新 |
| JMS | `activemq-all` → `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` |

### 4. XMLスキーマの変更（web.xml等）

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" ... version="3.1">
<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" ... version="6.0">
```

### 5. JSPタグライブラリのネームスペース変更

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 6. ツール・プラグインの更新

| ツール | 変更内容 |
|---|---|
| gsp-dba-maven-plugin | `5.1.0` に更新（Jakarta EE対応版） |
| waitt-maven-plugin | `jetty-ee10-maven-plugin:12.0.12` に変更 |
| nablarch-testing-jetty6 | `nablarch-testing-jetty12` に変更 |

テスト設定ファイルも変更が必要:
```xml
<!-- 修正前 -->
<component name="httpServerFactory" class="nablarch.fw.web.httpserver.HttpServerFactoryJetty6"/>
<!-- 修正後 -->
<component name="httpServerFactory" class="nablarch.fw.web.httpserver.HttpServerFactoryJetty12"/>
```

### 7. Jakarta Batchアプリケーション（JSR352）の追加対応

JBeretと関連ライブラリの更新が必要です（変更量が多く複雑）。`jboss-batch-api_1.0_spec` → `jakarta.batch:jakarta.batch-api` などへの変更が含まれます。

**注意点**:
- この手順はNablarch 5の**最新版**へのバージョンアップが完了していることが前提です
- Nablarch 6はJava 17以上が必須です
- **Jakarta EE 10対応のアプリケーションサーバ**が必要です（後方互換性なし）
- 6u3以降へバージョンアップする場合は、各バージョンのリリースノートで追加手順を確認してください
- `javax.crypto.*` のようなJava標準ライブラリの `javax` は変更不要です（Java EEの名前空間ではないため）

参照: `about/migration/migration-migration.json#s2`, `about/migration/migration-migration.json#s9`, `about/migration/migration-migration.json#s16`, `about/migration/migration-migration.json#s26`, `about/migration/migration-migration.json#s27`, `about/migration/migration-migration.json#s28`