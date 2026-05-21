Step 5: 回答を生成します。

**結論**: Nablarch 5からNablarch 6への移行では、Jakarta EE 10対応として主に「javax.*からjakarta.*への名前空間変更（コード・設定ファイル全体）」「Java EE依存関係のJakarta EE版への切り替え」「Jakarta EE 10対応アプリケーションサーバへの移行」「Java 17以上への環境変更」が必要です。

**根拠**:

移行で必要な作業は大きく2つに整理されます。

#### 1. 環境要件の変更

- **Javaバージョン**: Java 17以上が必要（Nablarch 6モジュールはJava 17でコンパイルされている）
- **アプリケーションサーバ**: Jakarta EE 10対応のアプリケーションサーバに変更が必要（名前空間変更により後方互換性なし）

#### 2. Nablarchのバージョンアップ（pom.xml）

`nablarch-bom` のバージョンを6に変更します。

#### 3. Java EE依存関係をJakarta EEに変更

Java EEのAPI依存関係をJakarta EE版に置き換えます。バージョン管理にはJakarta EEが提供するBOMの利用を推奨します。

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

変更対象の代表例：Java Servlet、JSP、JSTL、JPA、JAX-RS、Common Annotations

また、Java EE仕様の**実装ライブラリ**（Bean Validation実装のHibernate Validator、JAX-RS実装のJersy、JMS実装のActiveMQなど）もJakarta EE対応版に更新が必要です。

#### 4. アプリケーションコードの名前空間変更（最重要）

Jakarta EE 9で `javax.*` から `jakarta.*` への名前空間変更が行われたため、アプリケーションコード全体の対応が必要です。

**対応手順**:
1. `javax` でインポートしている箇所がコンパイルエラーになるので `jakarta` に変更
2. プロジェクト全体を `javax` でGrep検索し、コンパイルエラーにならない箇所も確認
3. Java EEの名前空間か判定（`javax.crypto.*` など標準ライブラリは変更不要）
4. Java EEの名前空間であれば `jakarta` に置換

変更例：
```java
// Before
import javax.validation.ConstraintValidator;
// After
import jakarta.validation.ConstraintValidator;
```

#### 5. XMLスキーマの変更

`web.xml` などのXMLファイルのスキーマ宣言を変更します。

```xml
<!-- Before -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
         http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
         version="3.1">

<!-- After -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

#### 6. JSPタグライブラリのネームスペース変更

```jsp
<%-- Before --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- After --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

#### 7. Nablarchの機能名称変更（名称のみ、機能変更なし）

| Nablarch 5までの名称 | Nablarch 6からの名称 |
|---|---|
| JAX-RS BeanValidationハンドラ | Jakarta RESTful Web Services Bean Validationハンドラ |
| JAX-RSアダプタ | Jakarta RESTful Web Servicesアダプタ |
| JAX-RSサポート | Jakarta RESTful Web Servicesサポート |
| JSPカスタムタグ | Jakarta Server Pagesカスタムタグ |
| JSR352に準拠したバッチアプリケーション | Jakarta Batchに準拠したバッチアプリケーション |

クラス・パッケージ名は後方互換を維持するため変更なし。

**注意点**:
- ETL基盤、帳票ライブラリ、ワークフローライブラリはNablarch 6では非サポートとなっています。これらを使用しているプロジェクトは別途対応が必要です。
- `waitt-maven-plugin` はJakarta EE非対応のため `jetty-ee10-maven-plugin` への変更が必要です。
- テストで `nablarch-testing-jetty6` / `nablarch-testing-jetty9` を使用している場合は `nablarch-testing-jetty12` への変更と、`HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` のコンポーネント定義変更が必要です。

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, releases-nablarch6-releasenote-6.json:s2, about-nablarch-jakarta-ee.json:s2

---