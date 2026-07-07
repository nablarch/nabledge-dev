# qa-14 — run-3

## 質問

Nablarch 5からNablarch 6にバージョンアップするとき、Jakarta EE 10対応でアプリケーションに影響がある変更は何か？

## 回答

**結論**: Nablarch 5 → 6 のJakarta EE 10対応では、主に「依存関係の置き換え」「名前空間の変更（`javax.*` → `jakarta.*`）」「設定ファイルのスキーマ更新」の3系統の変更が必要です。

---

**根拠**:

#### 1. 動作環境の変更（必須）

- **Java 17以上が必要**: Nablarch 6モジュールはJava 17でコンパイルされている
- **Jakarta EE 10対応のアプリケーションサーバが必要**: 名前空間変更などにより後方互換性が維持されない

#### 2. pom.xml: NablarchのBOMバージョン変更

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>   <!-- 5u** → 6u2 -->
  ...
</dependency>
```

#### 3. pom.xml: Java EE APIの依存関係をJakarta EEに変更

主な変更例：

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.apache.geronimo.specs:geronimo-jpa_2.0_spec` | `jakarta.persistence:jakarta.persistence-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

Jakarta EE BOMをまとめて読み込む方法を推奨：
```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

#### 4. pom.xml: 実装ライブラリのバージョン更新

| ライブラリ | 変更内容 |
|-----------|---------|
| Bean Validation | `org.hibernate:hibernate-validator:5.3.6.Final` → `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| JSTL | `taglibs:standard` → `org.glassfish.web:jakarta.servlet.jsp.jstl:3.0.0` |
| JAX-RS (Jersey) | `jersey-bom` のバージョンを3.1.8に更新 |
| JMS (ActiveMQ) | `activemq-all` → `artemis-server` / `artemis-jakarta-server` / `artemis-jakarta-client` |

#### 5. Javaソースコード・設定ファイル: javax名前空間をjakartaに変更

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

コンパイルエラーにならないケース（文字列指定）も存在するため、プロジェクト全体を `javax` でGrep検索して漏れなく対応する必要がある。

#### 6. web.xml等: XMLスキーマをJakarta EE 10に変更

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

#### 7. JSP: タグライブラリのネームスペースを変更

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

#### 8. テスト環境: Jettyモジュールの変更（ウェブアプリのみ）

```xml
<!-- 修正前 -->
<artifactId>nablarch-testing-jetty6</artifactId>

<!-- 修正後 -->
<artifactId>nablarch-testing-jetty12</artifactId>
```

合わせて `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` に変更する。

#### 9. Jakarta Batch（JBeret）を使っている場合の追加対応

JBeretと関連ライブラリの置き換えが必要（javax系→jakarta系への変更が複雑）。例：
- `org.jboss.spec.javax.batch:jboss-batch-api_1.0_spec` → `jakarta.batch:jakarta.batch-api`
- `javax.inject:javax.inject` → `jakarta.inject:jakarta.inject-api`
- `org.jboss.weld:weld-core` → `org.jboss.weld:weld-core-impl:5.0.1.Final`

**注意点**:
- `javax.crypto.SecretKeyFactory` など標準ライブラリの `javax` 名前空間はJava EEではないため変更不要
- waitt-maven-plugin（ウェブアプリのみ）は jetty-ee10-maven-plugin へ置き換えが必要
- gsp-dba-maven-plugin を使っている場合は5.1.0へ更新が必要

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s20, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29

## 参照ナレッジ

- [Jakarta EE 10に対応](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#jakarta-ee-10に対応) (s2)
- [動作に必要なJavaの最低バージョンを17に変更](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#動作に必要なjavaの最低バージョンを17に変更) (s3)
- [移行手順の概要](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#移行手順の概要) (s5)
- [Nablarchのバージョンアップ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#nablarchのバージョンアップ) (s7)
- [Java EEの依存関係をJakarta EEに変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#java-eeの依存関係をjakarta-eeに変更する) (s9)
- [Java EE仕様の実装ライブラリを更新する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#java-ee仕様の実装ライブラリを更新する) (s16)
- [Bean Validation → Jakarta Bean Validation](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#bean-validation-jakarta-bean-validation) (s17)
- [JSTL → Jakarta Standard Tag Library](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#jstl-jakarta-standard-tag-library) (s18)
- [JAX-RS → Jakarta RESTful Web Services](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#jax-rs-jakarta-restful-web-services) (s19)
- [JMS → Jakarta Messaging](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#jms-jakarta-messaging) (s20)
- [nablarch-testing-jetty6をnablarch-testing-jetty12に変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#nablarch-testing-jetty6をnablarch-testing-jetty12に変更する) (s25)
- [javax名前空間をjakarta名前空間に変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#javax名前空間をjakarta名前空間に変更する) (s26)
- [XMLスキーマ指定をJakarta EE 10のスキーマに変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#xmlスキーマ指定をjakarta-ee-10のスキーマに変更する) (s27)
- [タグライブラリのネームスペースをJakarta EE 10のネームスペースに変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#タグライブラリのネームスペースをjakarta-ee-10のネームスペースに変更する) (s28)
- [JSR352に準拠したバッチアプリケーションの移行手順](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#jsr352に準拠したバッチアプリケーションの移行手順) (s29)
- [Jakarta EE 10対応](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/releases/releases/releases-nablarch6-releasenote-6.md#jakarta-ee-10対応) (s2)
- [Nablarch5と6で名称が変更になった機能について](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/about-nablarch/about-nablarch-jakarta-ee.md#nablarch5と6で名称が変更になった機能について) (s2)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both facts from the Expected Output. It explicitly states that Jakarta EE 10対応のアプリケーションサーバが必要 (covering the first fact about requiring Jakarta EE 10 compatible application servers), and it thoroughly documents the namespace changes from javax.* to jakarta.* (covering the second fact about Java EE specification names and package names changing to Jakarta EE). Both expected facts are present and accurately represented without contradiction. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is perfectly relevant to the question about changes affecting applications when upgrading from Nablarch 5 to Nablarch 6 with Jakarta EE 10 support. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Jakarta EE 10対応のアプリケーションサーバで動作させる必要がある」は回答の「Jakarta EE 10対応のアプリケーションサーバが必要: 名前空間変更などにより後方互換性が維持されない」に含まれている。参照事実「Java EEの仕様名およびパッケージ名がJakarta EEのものに変更されている」は回答の依存関係変更表（javax.servlet → jakarta.servlet等）およびセクション5の名前空間変更説明に含まれている |
| answer_relevancy | OK | 回答はNablarch 5→6移行時のJakarta EE 10対応で必要な変更（動作環境変更、pom.xml変更、依存関係置き換え、名前空間変更、XMLスキーマ更新、タグライブラリ変更、Jettyモジュール変更、JBeret対応）を網羅的に説明しており、質問に直接答えている。的外れな内容は含まれていない。 |
| faithfulness | OK | 回答の各項目はナレッジ（migration-migration.md）の記述と一致している。BOMバージョン（6u2）、依存関係の変更テーブル（javax.servlet→jakarta.servlet等）、Jakarta EE BOMの読み込み推奨、Bean Validationのバージョン変更（5.3.6.Final→8.0.0.Final）、JSTLの変更、名前空間変更手順、XMLスキーマ変更（xmlns/version値）、タグライブラリのネームスペース変更、nablarch-testing-jetty6→jetty12の変更など、すべてナレッジの内容を正しく反映している。矛盾は見当たらない。 |

### 参照事実（expected_facts）

- Jakarta EE 10に対応しており、Jakarta EE 10対応のアプリケーションサーバで動作させる必要がある
- Java EEの仕様名およびパッケージ名がJakarta EEのものに変更されている
