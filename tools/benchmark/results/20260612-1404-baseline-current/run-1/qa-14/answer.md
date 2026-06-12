**結論**: Nablarch 5 → 6へのバージョンアップでJakarta EE 10対応が必要であり、アプリケーションへの影響は主に「`javax.*` → `jakarta.*` の名前空間変更」「Maven依存関係の更新」「XML/JSPの設定変更」の3つに分類される。

---

**根拠**:

#### 1. 名前空間の変更（`javax.*` → `jakarta.*`）

Jakarta EE 9で名前空間が `javax.*` から `jakarta.*` に変更された。これはアプリケーションコードにも影響する。

**対応手順：**
1. `import javax.xxx` でコンパイルエラーになる箇所を `jakarta.xxx` に変更する
2. プロジェクト全体を `javax` でGrep検索し、コンパイルエラーにならない箇所も確認する
3. Java EEの名前空間か判断し（例：`javax.crypto.SecretKeyFactory` は標準ライブラリなので変更不要）、Java EE仕様のものは `jakarta` に置換する

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

文字列リテラルにも注意が必要（例：`javax.servlet.forward.request_uri` → `jakarta.servlet.forward.request_uri`）。

---

#### 2. Maven依存関係の変更（pom.xml）

**Java EE APIをJakarta EE APIに変更する（主な例）：**

| 変更前 | 変更後 |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

Jakarta EEのBOMを読み込むことで個別バージョン指定の手間を省ける：

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**Java EE実装ライブラリの更新（主な例）：**

| 変更前 | 変更後 |
|---|---|
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| Jersey BOM (旧バージョン) | `org.glassfish.jersey:jersey-bom:3.1.8` |
| `org.apache.activemq:activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` |

---

#### 3. XML・JSPの設定変更

**XMLスキーマの変更（web.xml等）：**

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
         http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
         version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

**JSPタグライブラリのネームスペース変更：**

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

#### 4. Jakarta Batchバッチの場合（追加手順）

JBeretと関連ライブラリを全面的に更新する必要がある。

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
<!-- 他にもjakarta.inject-api、jakarta.enterprise.cdi-api等が必要 -->
```

---

#### 5. 開発ツール関連の変更

- **waitt-maven-plugin** → **jetty-ee10-maven-plugin**（ウェブアプリのローカル実行用）
- **nablarch-testing-jetty6/9** → **nablarch-testing-jetty12**（NTFの組み込みサーバ）
  - `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` への設定変更も必要
- **gsp-dba-maven-plugin** を 5.1.0 に更新（エンティティ生成のJakarta EE対応）

---

**注意点**:

- アプリケーションサーバをJakarta EE 10対応のものに変更する必要がある（後方互換性は維持されない）
- Java 17以上の実行環境が必要（Nablarch 6はJava 17でコンパイルされている）
- 移行手順はNablarch 6u2への移行を前提としている。6u3以降へバージョンアップする場合は、各バージョンのリリースノートで追加手順を確認すること
- Nablarch機能名も変更されているが（例：「JAX-RSサポート」→「Jakarta RESTful Web Servicesサポート」）、クラスやパッケージ名は変更されておらず後方互換が維持されている

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s21, migration-migration.json:s22, migration-migration.json:s23, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29, about-nablarch-jakarta-ee.json:s2