Step 5: 回答を生成します。

**結論**: Nablarch 5からNablarch 6へのバージョンアップで、Jakarta EE 10対応としてアプリケーションに影響する変更は主に「依存関係の置換（`javax.*` → `jakarta.*`）」「名前空間の変更」「アプリケーションサーバの変更」の3つです。

---

Step 6: Verifyを実行します。

主なNablarch固有の主張の検証:
1. 「Nablarch 6はJakarta EE 10に対応」→ s2に明記。✅ supported
2. 「`javax.*` から `jakarta.*` への名前空間変更」→ s2/s26に明記。✅ supported
3. 「Java 17以上が必要」→ s3に明記。✅ supported
4. 「BOMを`6u2`に変更する」→ s7に明記。✅ supported
5. 「`jakarta.platform:jakarta.jakartaee-bom:10.0.0` 推奨」→ s9に明記。✅ supported
6. 「`nablarch-testing-jetty6`を`nablarch-testing-jetty12`に変更」→ s25に明記。✅ supported（ただしs25はread対象外）
7. 「`waitt-maven-plugin`を`jetty-ee10-maven-plugin`に変更」→ s24に明記。✅ supported（ただしs24はread対象外）

s24とs25はread_sectionsに含めていないため、これらを根拠とした具体的な記述は避けます。

verify_result = PASS（read_sectionsから引用した内容のみで構成する）

---

**結論**: Jakarta EE 10対応でアプリケーションに影響する変更は、依存関係の置換・名前空間変更・アプリケーションサーバ変更の3点が中心です。

**根拠**:

### 1. Nablarchのバージョンアップ（pom.xml変更）

`pom.xml` でNablarchのBOMバージョンを`6u2`に変更します。

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.nablarch.profile</groupId>
      <artifactId>nablarch-bom</artifactId>
      <version>6u2</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

### 2. Java EEの依存関係をJakarta EEに置換

Java EEのAPIの`dependency`を、Jakarta EEのものに変更する必要があります。Jakarta EEが提供するBOMを読み込む方法が推奨されます。

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>jakarta.platform</groupId>
      <artifactId>jakarta.jakartaee-bom</artifactId>
      <version>10.0.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

具体的な変更例（抜粋）:

| 変更前 | 変更後 |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

### 3. Java EE仕様の実装ライブラリを更新

Bean ValidationのHibernate Validatorなど、Java EE仕様の実装ライブラリをJakarta EE対応版に置き換えます。

```xml
<!-- 変更前 -->
<dependency>
  <groupId>org.hibernate</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>5.3.6.Final</version>
</dependency>

<!-- 変更後 -->
<dependency>
  <groupId>org.hibernate.validator</groupId>
  <artifactId>hibernate-validator</artifactId>
  <version>8.0.0.Final</version>
</dependency>
```

### 4. `javax` 名前空間を `jakarta` 名前空間に変更

Javaソースコード・JSP・設定ファイル全体で、Java EEの `javax.*` 名前空間を `jakarta.*` に置換します。

対応の流れ:
1. `javax` でコンパイルエラーになる箇所を `jakarta` に変更する
2. プロジェクト全体を `javax` でGrep検索し、コンパイルエラーにならない箇所も網羅的に調査する（例: 文字列として現れる `javax.servlet.forward.request_uri`）
3. Java標準ライブラリの `javax.crypto` 等はJava EEではないため変更しない

```java
// 変更前
import javax.validation.ConstraintValidator;
// 変更後
import jakarta.validation.ConstraintValidator;
```

### 5. XMLスキーマ指定の変更（web.xml等）

`web.xml` 等のXMLファイルのスキーマ指定をJakarta EE 10のものに変更します。

```xml
<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

### 6. JSPのtaglibネームスペース変更

JSPファイルのtaglibディレクティブのURIをJakarta EE 10のものに変更します。

```jsp
<!-- 変更前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!-- 変更後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

**注意点**:
- Jakarta EE 9で入った名前空間の変更（`javax.*` → `jakarta.*`）は後方互換性が維持されないため、アプリケーションサーバもJakarta EE 10対応のものに変更する必要があります。
- Javaの最低バージョンが17に変更されているため、実行環境のJavaも17以上が必要です。
- `javax` がヒットしても、`javax.crypto`（Java標準ライブラリ）等はJava EEではないため変更対象外です。適切に判断してください。

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28

---