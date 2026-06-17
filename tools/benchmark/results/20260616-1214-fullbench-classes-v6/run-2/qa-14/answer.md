**結論**: Nablarch 5→6のJakarta EE 10対応で、アプリケーションには「名前空間の変更（`javax.*` → `jakarta.*`）」「依存関係の置き換え」「設定ファイルのスキーマ更新」「Java 17への移行」の4種類の影響がある。

---

**根拠**:

#### 1. アプリケーションサーバの要件変更

Jakarta EE 10に対応したアプリケーションサーバでなければ動作しない。また、Nablarch 6のモジュールはJava 17でコンパイルされているため、**実行環境のJavaバージョンを17以上にする必要がある**。

#### 2. Nablarchのバージョンアップ（BOM変更）

`pom.xml` でNablarch BOMのバージョンを変更する。

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>  <!-- 5系から変更 -->
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

#### 3. Java EE APIの依存関係 → Jakarta EE に変更

`groupId` が `javax.*` 系のものを `jakarta.*` 系に置き換える。代表的なもの：

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

バージョン管理の簡略化のため、Jakarta EEのBOMを読み込むことを推奨：

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

組み込んでいる実装ライブラリをJakarta EE対応版に更新する。代表例：

- **Bean Validation**: `org.hibernate:hibernate-validator:5.3.6.Final` → `org.hibernate.validator:hibernate-validator:8.0.0.Final`
- **JSTL実装**: `taglibs:standard` → `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0`
- **JAX-RS (Jersey)**: `jersey-bom` のバージョンを3.x系（例: 3.1.8）に更新
- **JMS (ActiveMQ)**: `activemq-all` → `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client`

#### 5. javax名前空間 → jakarta名前空間への変更（コード・設定ファイル）

Jakarta EE 9で名前空間が `javax.*` から `jakarta.*` に変更されたため、アプリケーションコードも修正が必要。

対応手順：
1. `import javax.***` でコンパイルエラーが出る箇所を `jakarta.***` に変更
2. **コンパイルエラーにならない場所も要確認**（文字列リテラル、JSP、設定ファイル内の `javax.servlet.forward.request_uri` など）
3. プロジェクト全体を `javax` でGrep検索し、Java EEの名前空間か（`javax.crypto` のような標準ライブラリではないか）を判定して置換

```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

> **注意**: `javax.crypto` のようなJava標準ライブラリの名前空間は変更不要。

#### 6. XMLスキーマ指定の変更（web.xml等）

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

#### 7. JSPのタグライブラリネームスペース変更（ウェブアプリケーション）

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

#### 8. テスト用組み込みサーバの変更（ウェブアプリケーション）

- **waitt-maven-plugin** → `jetty-ee10-maven-plugin:12.0.12` に変更
- **nablarch-testing-jetty6 / jetty9** → `nablarch-testing-jetty12` に変更（コンポーネント定義も `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12`）

#### 9. アダプタの更新

- **Domaアダプタ**: 依存関係の設定変更が必要
- **Micrometerアダプタ**: 監視サービスと連携している場合はMicrometerモジュールのバージョン更新が必要
- **gsp-dba-maven-plugin**: `5.1.0` に更新（Jakarta EEのアノテーションを持つEntityを生成するため）

#### 10. Jakarta Batchの特別対応（Jakarta Batchアプリケーションのみ）

JBeretと関連ライブラリの更新が複雑：

```xml
<!-- 修正後の主要な依存関係 -->
<dependency><groupId>jakarta.batch</groupId><artifactId>jakarta.batch-api</artifactId></dependency>
<dependency><groupId>jakarta.inject</groupId><artifactId>jakarta.inject-api</artifactId></dependency>
<dependency><groupId>org.jberet</groupId><artifactId>jberet-core</artifactId><version>2.1.4.Final</version></dependency>
<dependency><groupId>org.jboss.weld</groupId><artifactId>weld-core-impl</artifactId><version>5.0.1.Final</version></dependency>
<dependency><groupId>org.jberet</groupId><artifactId>jberet-se</artifactId><version>2.1.4.Final</version></dependency>
```

#### 11. Nablarch機能名称の変更

以下の機能は名称変更のみ（クラス名・パッケージ名は後方互換のため変更なし）：

| Nablarch 5までの名称 | Nablarch 6からの名称 |
|---------------------|---------------------|
| JAX-RS BeanValidationハンドラ | Jakarta RESTful Web Services Bean Validationハンドラ |
| JAX-RSアダプタ | Jakarta RESTful Web Servicesアダプタ |
| JSPカスタムタグ | Jakarta Server Pagesカスタムタグ |
| JSR352に準拠したバッチアプリケーション | Jakarta Batchに準拠したバッチアプリケーション |

---

**注意点**: 移行手順は6u2への移行を前提としている。6u3以降へのバージョンアップでは追加手順が必要なため、各バージョンのリリースノートを順に確認すること。

参照:
- migration-migration.json:s2, s3, s5, s7, s9, s16, s26, s27, s28, s29
- releases/releases/releases-nablarch6-releasenote-6.json:s2, s3
- about/about-nablarch/about-nablarch-jakarta-ee.json:s2