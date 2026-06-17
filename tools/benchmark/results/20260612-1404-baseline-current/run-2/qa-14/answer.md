**結論**: Nablarch 5からNablarch 6へのバージョンアップでは、Jakarta EE 10対応（`javax.*` → `jakarta.*` 名前空間変更）とJava 17への移行が必須であり、アプリケーションコード・設定ファイル・依存関係のすべてに変更が必要です。後方互換性は維持されないため、Jakarta EE 10対応のアプリケーションサーバへの移行も必要となります。

---

**根拠**:

#### 1. 環境要件の変更

- **Java 17以上が必須**: Nablarch 6のモジュールはJava 17でコンパイルされているため、実行環境のJavaバージョンを17にする必要があります。
- **Jakarta EE 10対応アプリケーションサーバが必要**: 名前空間の変更により後方互換性が維持されないため、Jakarta EE 10対応のアプリケーションサーバが必要です。

#### 2. `pom.xml` の依存関係変更

**NablarchのBOM更新**:
```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>  <!-- 5.x → 6u2 -->
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**Jakarta EE BOM の追加（推奨）**:
```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**Java EE APIをJakarta EEに変更（例）**:

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

**実装ライブラリの更新（例）**:
- Bean Validation実装: `org.hibernate:hibernate-validator:5.x` → `org.hibernate.validator:hibernate-validator:8.0.0.Final`
- JSTL実装: `taglibs:standard` → `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0`
- JAX-RS実装(Jersey): BOMを `jersey-bom:3.1.8` に更新

#### 3. アプリケーションコード（`javax` → `jakarta` 名前空間変更）

**手順**:
1. `javax.*` でimportしていた箇所がコンパイルエラーになるため `jakarta.*` に変更
2. プロジェクト全体を `javax` でGrep検索し、コンパイルエラーにならない箇所も確認
3. Java EEの名前空間か判断してから `jakarta` に置換

**例**:
```java
// 変更前
import javax.validation.ConstraintValidator;

// 変更後
import jakarta.validation.ConstraintValidator;
```

**注意**: 文字列として記述された `javax.servlet.forward.request_uri` のような定数もJakarta Servletでは `jakarta.servlet.forward.request_uri` に変更が必要です。一方、`javax.crypto.SecretKeyFactory` のような標準ライブラリの `javax.*` はJava EEとは無関係のため変更不要です。

#### 4. 設定ファイルの変更

**XMLスキーマ指定（web.xml等）**:
```xml
<!-- 変更前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
         http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
         version="3.1">

<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

**JSPのtaglibネームスペース**:
```jsp
<%-- 変更前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 変更後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

#### 5. ウェブプロジェクト固有の変更

- **waitt-maven-plugin → jetty-ee10-maven-plugin**: waitt-maven-pluginはJakarta EE非対応のため、`org.eclipse.jetty.ee10:jetty-ee10-maven-plugin:12.0.12` に変更します。
- **nablarch-testing-jetty6 → nablarch-testing-jetty12**: NTFの組み込みサーバを `nablarch-testing-jetty12` に変更し、コンポーネント定義の `HttpServerFactoryJetty6` を `HttpServerFactoryJetty12` に変更します。

#### 6. Jakarta Batch（JSR352）アプリケーション固有の変更

JBeret関連ライブラリをJakarta EE対応版に変更する必要があります（変更内容が複雑なため個別に確認が必要）。主な変更点：

| 変更前 | 変更後 |
|--------|--------|
| `org.jboss.spec.javax.batch:jboss-batch-api_1.0_spec` | `jakarta.batch:jakarta.batch-api` |
| `javax.inject:javax.inject` | `jakarta.inject:jakarta.inject-api` |
| `org.jberet:jberet-core` (旧バージョン) | `org.jberet:jberet-core:2.1.4.Final` |
| `org.jboss.weld:weld-core` | `org.jboss.weld:weld-core-impl:5.0.1.Final` |

---

**注意点**:

- Nablarch 5の**最新版**へのバージョンアップを完了してからNablarch 6への移行を行うこと（古いバージョンからは直接移行不可）。
- **ETL基盤・帳票ライブラリ・ワークフローライブラリ**はNablarch 6に非対応のため解説書から削除されています。これらを使用しているアプリケーションは別途対処が必要です。
- 6u3以降へのバージョンアップが必要な場合は、本ガイドの手順に加えて各リリースノートの追加手順も確認すること。

参照:
- migration-migration.json:s2, s3, s7, s26, s27, s28, s29
- releases-nablarch6-releasenote-6.json:s2, s3