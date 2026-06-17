**結論**: Nablarch 5からNablarch 6へのJakarta EE 10対応では、「依存関係のJakarta EE版への変更」「javax名前空間のjakarta名前空間への置換」「XMLスキーマ・タグライブラリネームスペースの更新」「各種プラグインの更新」が必要です。実行環境もJava 17以上・Jakarta EE 10対応APサーバへの変更が求められます。

---

**根拠**:

### 1. Nablarch BOMのバージョンを変更する

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>  <!-- 5.x.x → 6u2 -->
  ...
</dependency>
```

### 2. Java EEの依存関係をJakarta EEに変更する

Jakarta EE BOMを読み込むことが推奨されます。

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

主な変更例：

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

### 3. Java EE仕様の実装ライブラリを更新する

| ライブラリ | 変更前 | 変更後 |
|-----------|--------|--------|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL実装 | `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS (Jersey) | BOM旧バージョン | `org.glassfish.jersey:jersey-bom:3.1.8` |
| JMS (ActiveMQ) | `activemq-all` | `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client` (各2.37.0) |

### 4. javax名前空間をjakarta名前空間に変更する

Javaソースコードの `import` 文でコンパイルエラーになった箇所から対応を開始し、プロジェクト全体を `javax` でGrep検索して残りを修正します。

```java
// 変更前
import javax.validation.ConstraintValidator;

// 変更後
import jakarta.validation.ConstraintValidator;
```

文字列リテラルにも `javax` が含まれる場合があります（例：`javax.servlet.forward.request_uri` → `jakarta.servlet.forward.request_uri`）。

**注意**: `javax.crypto.*` など標準ライブラリの `javax` はJava EEの名前空間ではないため変更不要です。

### 5. XMLスキーマ指定を変更する（web.xml等）

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

### 6. タグライブラリネームスペースを変更する（JSP）

```jsp
<%-- 変更前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 変更後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 7. 各種プラグインを更新する

- **gsp-dba-maven-plugin**: `5.1.0` に更新（Jakarta EEアノテーション対応のエンティティ生成）
- **waitt-maven-plugin** → **jetty-ee10-maven-plugin** に変更（ウェブプロジェクトのみ）

```xml
<!-- 変更後 -->
<plugin>
  <groupId>org.eclipse.jetty.ee10</groupId>
  <artifactId>jetty-ee10-maven-plugin</artifactId>
  <version>12.0.12</version>
</plugin>
```

- **nablarch-testing-jetty6** → **nablarch-testing-jetty12** に変更（ウェブプロジェクトのテストのみ）

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-testing-jetty12</artifactId>
  <scope>test</scope>
</dependency>
```

合わせて `HttpServerFactory` のクラスも変更が必要です：

```xml
<!-- 変更後 -->
<component name="httpServerFactory" class="nablarch.fw.web.httpserver.HttpServerFactoryJetty12"/>
```

### 8. Jakarta Batchの場合の追加対応

Jakarta Batchアプリケーションではさらに、JBeretと関連ライブラリをJakarta EE対応版に更新する必要があります（jberet-core:2.1.4.Final、weld-core-impl:5.0.1.Finalなど）。

---

**注意点**:
- 実行環境のJavaバージョンを **Java 17以上** に変更する必要があります
- アプリケーションサーバを **Jakarta EE 10対応版** に変更する必要があります
- 手順は Nablarch 5最新版へのバージョンアップが完了していることが前提です
- 6u3以降へバージョンアップする場合は、本手順に加えて6u3以降のリリースノートも確認が必要です

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s10, migration-migration.json:s11, migration-migration.json:s12, migration-migration.json:s13, migration-migration.json:s14, migration-migration.json:s15, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s20, migration-migration.json:s23, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29