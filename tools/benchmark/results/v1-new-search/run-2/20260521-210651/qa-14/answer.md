Step 4で取得したセクション内容を確認しました。Step 5〜8で回答を生成します。

---

**結論**: Nablarch 5→6のJakarta EE 10対応では、(1) `javax.*` 名前空間を `jakarta.*` に全面置換、(2) Java EE依存関係をJakarta EE版に変更、(3) `web.xml`等のXMLスキーマとJSPタグライブラリのネームスペースを更新、の3点が主なアプリケーションへの影響です。また、実行環境をJava 17以上かつJakarta EE 10対応のアプリケーションサーバに変更する必要があります。

---

**根拠**:

### 1. Nablarch BOMのバージョン変更

`pom.xml` のNablarch BOMバージョンを `6u2` に変更します：

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

### 2. Java EE依存関係 → Jakarta EE依存関係への変更

Jakarta EE BOMをインポートしてバージョン管理を一元化することを推奨します：

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

代表的な変更内容：

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `taglibs:standard`（JSTL実装） | `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| Jersey BOM（旧バージョン） | `org.glassfish.jersey:jersey-bom:3.1.8` |

### 3. javax名前空間 → jakarta名前空間への変更

Javaソースコードの `import` 文や設定ファイルの文字列参照を変更します：

```java
// 変更前
import javax.validation.ConstraintValidator;

// 変更後
import jakarta.validation.ConstraintValidator;
```

注意点：コンパイルエラーにならない箇所（文字列として記述されているもの）も変更対象です。例えば：

```
javax.servlet.forward.request_uri
→ jakarta.servlet.forward.request_uri
```

プロジェクト全体を `javax` でGrep検索し、Java EEの名前空間かどうかを判定してから `jakarta` に置換します（`javax.crypto.*` などJava標準ライブラリの `javax` は変更不要）。

### 4. XMLスキーマ指定の変更

`web.xml` 等のXMLファイルのスキーマを Jakarta EE 10 のものに更新します：

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

### 5. JSPタグライブラリのネームスペース変更

```jsp
<!-- 変更前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 変更後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 6. Jakarta Batch（JBeret）の依存関係変更

Jakarta Batchに準拠したバッチアプリケーション（旧JSR352）では、JBeret関連ライブラリの更新が特に複雑で、`jakarta.batch:jakarta.batch-api`、`jakarta.inject:jakarta.inject-api`、`jberet-core:2.1.4.Final` 等への全面的な変更が必要です。

---

**注意点**:
- **ETL基盤・帳票ライブラリ・ワークフローライブラリ**はNablarch 6に非対応のため、これらを使用しているアプリケーションは別途対応方針の検討が必要です。
- 移行手順の前提として、まずNablarch 5の最新版へのバージョンアップが完了している必要があります。

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29, releases-nablarch6-releasenote-6.json:s2, releases-nablarch6-releasenote-6.json:s9, releases-nablarch6-releasenote-6.json:s11, releases-nablarch6-releasenote-6.json:s13

---