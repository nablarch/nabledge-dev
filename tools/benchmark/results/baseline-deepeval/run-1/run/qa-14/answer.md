**結論**: Nablarch 5から6への移行でJakarta EE 10対応が必要な変更は、主に「依存ライブラリの更新」「`javax` → `jakarta` 名前空間の置換」「設定ファイルのスキーマ変更」「開発ツールの更新」の4カテゴリです。

---

**根拠**:

#### 1. 前提: 最低JavaバージョンがJava 17に変更

Nablarch 6のモジュールはJava 17でコンパイルされているため、実行環境をJava 17以上に変更する必要があります。

#### 2. Nablarchのバージョンアップ（BOM変更）

`pom.xml` の `nablarch-bom` のバージョンを 6系 に変更します。

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

#### 3. Java EE APIの依存関係をJakarta EEに変更

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

Jakarta EEのBOMを読み込むことで個別バージョン指定を省略できます。

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

#### 4. Java EE仕様の実装ライブラリを更新

| 変更前 | 変更後 |
|--------|--------|
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| Jersey BOM (旧バージョン) | Jersey BOM `3.1.8` |
| `org.apache.activemq:activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` (JMSを使う場合) |

#### 5. ソースコード: `javax` 名前空間を `jakarta` に変更

Jakarta EE 9で名前空間が `javax.*` から `jakarta.*` に変更されました。

1. `import` 文のコンパイルエラー箇所を `jakarta` に修正する
2. プロジェクト全体を `javax` でGrep検索し、Java EEの名前空間か確認する
3. Java EEの名前空間であれば `jakarta` に置換する（標準ライブラリの `javax.crypto` 等は置換不要）

```java
// 変更前
import javax.validation.ConstraintValidator;

// 変更後
import jakarta.validation.ConstraintValidator;
```

#### 6. XMLスキーマの変更

`web.xml` 等のスキーマをJakarta EE 10対応に変更します。

```xml
<!-- 変更前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         version="3.1">

<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee web-app_6_0.xsd"
         version="6.0">
```

#### 7. JSP taglibネームスペースの変更

```jsp
<!-- 変更前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 変更後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

#### 8. 開発ツールの変更（ウェブプロジェクト）

- **waitt-maven-plugin** → **jetty-ee10-maven-plugin** (`org.eclipse.jetty.ee10:jetty-ee10-maven-plugin:12.0.12`)
- **nablarch-testing-jetty6** → **nablarch-testing-jetty12**、コンポーネント設定の `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12`

#### 9. Jakarta Batch使用プロジェクトの追加対応

`javax.batch` 系の依存関係を `jakarta.batch:jakarta.batch-api` 等に変更し、JBeret (`jberet-core:2.1.4.Final`)・Weld (`weld-core-impl:5.0.1.Final`) 等の関連ライブラリをJakarta EE対応版に更新します。

---

**注意点**:
- アプリケーションサーバ自体もJakarta EE 10対応のもの（Tomcat 10以降、WildFly 27以降等）に変更が必要です。
- `javax` でのGrep検索では、Java標準ライブラリ（`javax.crypto`、`javax.sql` 等）はJava EEの名前空間ではないため置換対象外です。
- Nablarchが提供するハンドラ・アダプタの名称は変更されますが（「JAX-RS」→「Jakarta RESTful Web Services」等）、クラス・パッケージ名は後方互換性のため変更されていません。

参照: about/migration/migration-migration.json:s2, about/migration/migration-migration.json:s3, about/migration/migration-migration.json:s5, about/migration/migration-migration.json:s9, about/migration/migration-migration.json:s10, about/migration/migration-migration.json:s11, about/migration/migration-migration.json:s12, about/migration/migration-migration.json:s13, about/migration/migration-migration.json:s14, about/migration/migration-migration.json:s15, about/migration/migration-migration.json:s16, about/migration/migration-migration.json:s17, about/migration/migration-migration.json:s18, about/migration/migration-migration.json:s19, about/migration/migration-migration.json:s20, about/migration/migration-migration.json:s24, about/migration/migration-migration.json:s25, about/migration/migration-migration.json:s26, about/migration/migration-migration.json:s27, about/migration/migration-migration.json:s28, about/migration/migration-migration.json:s29, releases/releases/releases-nablarch6-releasenote-6.json:s2, about/about-nablarch/about-nablarch-jakarta-ee.json:s2

---