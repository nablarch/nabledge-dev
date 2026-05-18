**結論**: Nablarch 5からNablarch 6へ移行する際、Jakarta EE 10対応としてアプリケーションに必要な変更は主に4つあります。①Java EE APIの依存関係をJakarta EE版に変更、②`javax.*` 名前空間を `jakarta.*` に変更、③XMLスキーマ指定をJakarta EE 10用に変更、④JSPのタグライブラリネームスペースを変更。

**根拠**:

### 1. Java EE APIの依存関係変更（`pom.xml`）

Jakarta EEが提供するBOMを読み込むことで、個別バージョン指定を省略できます。

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

### 2. `javax` 名前空間 → `jakarta` 名前空間への変更

**手順**:
1. `javax` でプロジェクト全体をGrep検索
2. ヒットした箇所がJava EEの名前空間かどうか判定（標準ライブラリの `javax.crypto` 等は対象外）
3. Java EEの名前空間であれば `javax` → `jakarta` に置換

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

文字列リテラル内の名前空間（例: `javax.servlet.forward.request_uri`）もコンパイルエラーにならないため、Grepで検索して手動対応が必要です。

### 3. XMLスキーマ指定の変更（`web.xml` 等）

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

### 4. JSP タグライブラリネームスペースの変更

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 5. Jakarta Batchアプリケーションの追加対応

JSR352に準拠したバッチアプリケーションを使用している場合、JBeretと関連ライブラリの更新が複雑なため個別対応が必要です。例: `jboss-batch-api_1.0_spec` → `jakarta.batch-api`、`weld-core` → `weld-core-impl:5.0.1.Final` など。

### 6. Nablarchの機能名称変更（後方互換あり）

クラス・パッケージ名は変更なし（後方互換維持）ですが、ドキュメント上の名称が変更されています。

| Nablarch 5までの名称 | Nablarch 6からの名称 |
|---|---|
| JAX-RS BeanValidationハンドラ | Jakarta RESTful Web Services Bean Validationハンドラ |
| JAX-RSアダプタ | Jakarta RESTful Web Servicesアダプタ |
| JSPカスタムタグ | Jakarta Server Pagesカスタムタグ |
| JSR352に準拠したバッチアプリケーション | Jakarta Batchに準拠したバッチアプリケーション |

**注意点**:
- Jakarta EE 10対応のアプリケーションサーバが必要（後方互換なし）
- `javax` 検索でヒットしても、`javax.crypto` 等の標準ライブラリは **変更不要**（Java EE名前空間でないため）
- Java EE仕様の実装ライブラリ（Bean Validation実装、JAX-RS実装等）も個別に調査してJakarta EE対応版に置き換える必要があります
- Java 17以上が前提のため、Nablarch 5時代にJava 17対応で追加した依存関係は不要になっている場合があります（`dependency:tree`で確認推奨）

参照: `about/migration/migration-migration.json#s2`, `about/migration/migration-migration.json#s5`, `about/migration/migration-migration.json#s9`, `about/migration/migration-migration.json#s16`, `about/migration/migration-migration.json#s26`, `about/migration/migration-migration.json#s27`, `about/migration/migration-migration.json#s28`, `about/migration/migration-migration.json#s29`, `about/about-nablarch/about-nablarch-jakarta-ee.json#s2`, `about/migration/migration-migration.json#s33`