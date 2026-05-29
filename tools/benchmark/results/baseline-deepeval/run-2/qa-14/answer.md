Step 5 で回答を生成し、Step 6 でverifyします。

---

**結論**: Nablarch 5 → 6 のバージョンアップでJakarta EE 10対応が必要であり、アプリケーションへの影響は「Nablarch BOMの更新」「Java EE依存関係のJakarta EE化」「`javax`→`jakarta`名前空間の置換」「XMLスキーマ・タグライブラリのネームスペース変更」の4カテゴリに分類されます。

---

**根拠**:

### 前提条件の変更

- **Java 17以上が必須**: Nablarch 6モジュールはJava 17でコンパイルされているため、実行環境を17以上に変更する必要がある
- **Jakarta EE 10対応アプリケーションサーバが必須**: 名前空間の変更などにより後方互換性が維持されないため

---

### 1. Nablarch BOMのバージョン変更

`pom.xml` の `nablarch-bom` バージョンを `6u2` 以降に変更する（Nablarch 6 / 6u1 は先行リリースのため、`6u2` が正式リリース後の最初のバージョン）。

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

---

### 2. Java EE依存関係をJakarta EEのものに変更

代表的な変更例（Jakarta EEのBOMを読み込む方法を推奨）:

```xml
<!-- Jakarta EE BOM の追加（推奨） -->
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard` | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |

---

### 3. `javax` 名前空間を `jakarta` 名前空間に変更

Jakarta EE 9で名前空間が `javax.*` → `jakarta.*` に変更されており、アプリケーションコード全体への対応が必要。

**手順**:
1. `javax` でコンパイルエラーが発生した箇所を `jakarta` に変更
2. プロジェクト全体をGrep検索し、コンパイルエラーにならない箇所も対応
3. Java EEの名前空間のみ置換（標準ライブラリの `javax.crypto` などは対象外）

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

注意点: JSPや設定ファイル内の文字列（例: `javax.servlet.forward.request_uri`）もコンパイルエラーにならないが修正が必要。

---

### 4. XMLスキーマ指定を Jakarta EE 10 のスキーマに変更

`web.xml` 等のXMLファイルのスキーマ宣言を変更する。

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee web-app_3_1.xsd"
         version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee web-app_6_0.xsd"
         version="6.0">
```

---

### 5. JSPタグライブラリのネームスペース変更

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

### 6. テスト用組み込みサーバの変更（ウェブアプリケーションのみ）

Nablarch Testing Framework使用時、Jetty 6/9はJakarta EE非対応のため `nablarch-testing-jetty12` に変更する。

```xml
<!-- pom.xml -->
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-testing-jetty12</artifactId>
  <scope>test</scope>
</dependency>
```

```xml
<!-- unit-test.xml -->
<!-- 修正前 -->
<component name="httpServerFactory" class="nablarch.fw.web.httpserver.HttpServerFactoryJetty6"/>

<!-- 修正後 -->
<component name="httpServerFactory" class="nablarch.fw.web.httpserver.HttpServerFactoryJetty12"/>
```

---

**注意点**:
- Nablarch 6/6u1は先行リリースであり、`6u2` からが正式リリース後の最初のバージョン。移行は `6u2` 以降への移行を前提に行うこと
- `6u3` 以降へバージョンアップする場合は、追加の手順が必要な場合があるため各リリースノートを順に確認すること
- `javax.crypto` など標準ライブラリの `javax` は置換対象外

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s25

---