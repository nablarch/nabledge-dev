これで必要な情報が揃いました。回答を生成します。

---

**結論**: Nablarch 5から6へのバージョンアップでは、Jakarta EE 10対応として「依存関係の`javax`→`jakarta`への変更」「Java EEのAPIをJakarta EE版に置き換え」「ソースコード・設定ファイル内の`javax`名前空間の`jakarta`への置換」の3つがアプリケーションへの主な影響です。また、動作にはJava 17以上とJakarta EE 10対応のアプリケーションサーバが必要になります。

---

**根拠**:

**1. Nablarchのバージョンアップ（pom.xml）**

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>  <!-- 5系のバージョンから変更 -->
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**2. Java EEのAPI依存関係をJakarta EE版に変更する**

代表的なもの：

| 変更前（Java EE） | 変更後（Jakarta EE） |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

BOMを利用してバージョン管理する場合：
```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**3. Java EE仕様の実装ライブラリをJakarta EE版に更新する**

| 仕様 | 変更前 | 変更後 |
|---|---|---|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL | `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS (Jersey) | `jersey-bom` 旧バージョン | `jersey-bom:3.1.8` |
| JMS | `activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` (各 2.37.0) |

**4. ソースコード内の`javax`名前空間を`jakarta`に変更する**

Jakarta EE 9から名前空間が`javax.*`から`jakarta.*`に変更された。

```java
// 変更前
import javax.validation.ConstraintValidator;

// 変更後
import jakarta.validation.ConstraintValidator;
```

コンパイルエラーにならない箇所（文字列定数、JSP、XML設定ファイル）も対象。例：
- `javax.servlet.forward.request_uri` → `jakarta.servlet.forward.request_uri`

注意: `javax.crypto.SecretKeyFactory`などJava標準ライブラリのクラスは置換対象外。

**5. web.xmlなどのXMLスキーマをJakarta EE 10のものに変更する**

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

**6. JSPのタグライブラリのネームスペースを変更する**

```jsp
<!-- 変更前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 変更後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

**7. ウェブアプリケーション固有の変更**

- `waitt-maven-plugin` → `jetty-ee10-maven-plugin:12.0.12`（Jakarta EE非対応のため）
- `nablarch-testing-jetty6` → `nablarch-testing-jetty12`（テスト用組み込みサーバ）
  - `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` にコンポーネント設定も変更

**8. Jakarta Batchアプリケーション固有の変更**

JBeretおよび関連ライブラリの更新が必要（依存関係が複雑）：
- `jberet-core:2.1.4.Final`、`jberet-se:2.1.4.Final`
- `weld-core-impl:5.0.1.Final`（`weld-se-core:5.0.1.Final`）
- `jakarta.batch:jakarta.batch-api`（`jboss-batch-api_1.0_spec`から変更）

---

**注意点**:
- 移行前にNablarch 5の最新版へのバージョンアップを完了しておくこと
- 実行環境をJava 17以上にする必要がある
- Jakarta EE 10対応のアプリケーションサーバ（Tomcat 10以降など）が必要
- 正式リリースはNablarch 6u2から。6u3以降へのバージョンアップには追加の手順が必要な場合があるため、リリースノートを順に参照すること
- Domaアダプタ・Micrometerアダプタを使用している場合は別途更新が必要
- gsp-dba-maven-pluginを使用している場合はバージョン5.1.0へ更新が必要

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29

---