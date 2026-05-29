内容が揃いました。Step 5〜7を実行して回答を生成します。

---

**結論**: Nablarch 5→6への移行で Jakarta EE 10 対応として必要な変更は、大きく「依存関係の更新」「`javax` → `jakarta` 名前空間の置換」「XMLスキーマ・タグライブラリネームスペースの変更」の3つです。また Java 17 以上が必須になります。

---

**根拠**:

### 1. 必要 Java バージョンの変更

Nablarch 6 のモジュールは Java 17 でコンパイルされているため、実行環境を **Java 17 以上**にする必要があります。

---

### 2. Nablarch BOM のバージョンアップ

`pom.xml` の `nablarch-bom` バージョンを変更します。

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>   <!-- 5u25 → 6u2 に変更 -->
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

---

### 3. Java EE API の依存関係を Jakarta EE に変更

主要な変更例：

| 修正前 | 修正後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

Jakarta EE BOM を一括で読み込む方法が推奨されます：

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

---

### 4. Java EE 実装ライブラリの更新

代表例：

**Bean Validation**
```xml
<!-- 修正前 -->
<dependency>
  <groupId>org.hibernate</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>5.3.6.Final</version>
</dependency>
<!-- 修正後 -->
<dependency>
  <groupId>org.hibernate.validator</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>8.0.0.Final</version>
</dependency>
```

**JSTL**
```xml
<!-- 修正前 -->
<dependency>
  <groupId>taglibs</groupId>
  <artifactId>standard</artifactId>
</dependency>
<!-- 修正後 -->
<dependency>
  <groupId>org.glassfish.web</groupId>
  <artifactId>jakarta.servlet.jsp.jstl</artifactId>
  <version>3.0.0</version>
</dependency>
```

**JAX-RS（Jerseyの場合）**
```xml
<!-- BOM を jersey-bom 3.1.8 以降に変更 -->
```

---

### 5. `javax` 名前空間 → `jakarta` 名前空間への変更

アプリケーションのソースコード・JSP・設定ファイル全体に対して `javax` を検索し、Java EE の名前空間であるものを `jakarta` に置換します。

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

注意：`javax.crypto.SecretKeyFactory` のような Java SE 標準ライブラリの `javax` は置換不要です。

---

### 6. XML スキーマの変更

`web.xml` 等の XML ファイルのスキーマ指定を Jakarta EE 10 対応に変更します：

```xml
<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

---

### 7. JSP タグライブラリのネームスペース変更

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

### 8. Jakarta Batch（JBeret）の更新（Jakarta Batch 使用時のみ）

JSR352（Jakarta Batch）を使用している場合、JBeret 関連の依存関係を全面的に更新する必要があります（`javax.*` 系の groupId を `jakarta.*` 系に変更、バージョンも刷新）。

---

**注意点**:
- `waitt-maven-plugin` はJakarta EE 未対応のため、`jetty-ee10-maven-plugin` (version 12.0.12) への置き換えが必要です（ウェブアプリケーションのみ）
- テストで `nablarch-testing-jetty6` または `nablarch-testing-jetty9` を使用している場合は `nablarch-testing-jetty12` に変更し、`HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` のコンポーネント設定も更新が必要です
- `gsp-dba-maven-plugin` を使用している場合はバージョン `5.1.0` 以上に更新が必要です

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29

---