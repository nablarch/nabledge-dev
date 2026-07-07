# qa-14 — run-1

## 質問

Nablarch 5からNablarch 6にバージョンアップするとき、Jakarta EE 10対応でアプリケーションに影響がある変更は何か？

## 回答

**結論**: Jakarta EE 10対応では「名前空間の`javax.*`→`jakarta.*`変更」を中心に、依存ライブラリの更新・XMLスキーマ変更・ツール類の置き換えなど、アプリケーション全体にわたる修正が必要です。後方互換性は維持されません。

---

**根拠**:

## 1. 名前空間の変更（全プロジェクト共通・最重要）

Jakarta EE 9でパッケージ名が `javax.*` から `jakarta.*` に変更されました。Javaコード・JSP・設定ファイルのすべてが対象です。

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

注意: `javax.crypto.SecretKeyFactory` のような Java標準ライブラリの `javax.*` は対象外です。プロジェクト全体をGrepして Java EEの名前空間か否かを判断する必要があります。

---

## 2. Java EE API依存関係をJakarta EEへ変更

`pom.xml` のdependencyをJakarta EE版に差し替えます。Jakarta EE BOMを導入してバージョン管理を一元化することを推奨します。

```xml
<!-- BOM追加（推奨） -->
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

主な変更例:

| Java EE (修正前) | Jakarta EE (修正後) |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `jakarta.ws.rs`へ変更 | `javax.ws.rs:javax.ws.rs-api` → `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |
| `javax.persistence` (JPA) | `jakarta.persistence:jakarta.persistence-api` |

---

## 3. Java EE実装ライブラリの更新

主な変更:

**Bean Validation（hibernate-validator）**:
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

**JSTL実装**:
```xml
<!-- 修正後 -->
<dependency>
  <groupId>org.glassfish.web</groupId>
  <artifactId>jakarta.servlet.jsp.jstl</artifactId>
  <version>3.0.0</version>
</dependency>
```

**JAX-RS実装（Jersey）**: jersey-bomのバージョンを3.1.8以降に変更。

**JMS実装（ActiveMQ）**: `activemq-all` → `artemis-server` + `artemis-jakarta-server` + `artemis-jakarta-client`。

---

## 4. XMLスキーマ変更（web.xml等）

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

---

## 5. JSPのタグライブラリネームスペース変更

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

## 6. ツール類の更新

| 修正前 | 修正後 | 対象 |
|---|---|---|
| `waitt-maven-plugin` | `jetty-ee10-maven-plugin 12.0.12` | ウェブプロジェクトの組み込みサーバ起動 |
| `nablarch-testing-jetty6`（または jetty9） | `nablarch-testing-jetty12` + `HttpServerFactoryJetty12` | NTFのテスト用組み込みサーバ |
| `gsp-dba-maven-plugin` | バージョン 5.1.0（Jakarta EE対応版） | エンティティクラス生成 |

---

## 7. Domaアダプタ・Micrometerアダプタの更新

- **Domaアダプタ**: 依存関係の設定変更と推奨実装方法への移行が必要
- **Micrometerアダプタ**: 監視サービス連携ライブラリのバージョン更新が必要

---

## 8. Jakarta Batch（JBeret）のみ追加の移行手順

JBeretとその関連ライブラリ（weld-core等）をJakarta EE対応版へ全面的に置き換えます。`javax.el:glassfish` → `expressly 5.0.0`、`jberet-core` → 2.1.4.Final など多数の依存関係変更が必要です。

---

**注意点**:
- 名前空間変更により後方互換性は一切維持されません。Jakarta EE 10対応のアプリケーションサーバ（Tomcat 10以降等）が必要です
- 動作にはJava 17以上が必要です
- 移行手順はNablarch 5の最新版（5u25相当）からNablarch 6u2へのアップグレードを前提としています。6u3以降へのバージョンアップには追加手順が必要なため、各リリースノートを確認してください

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s20, migration-migration.json:s21, migration-migration.json:s22, migration-migration.json:s23, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29, about-nablarch-jakarta-ee.json:s2

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
- [Domaアダプタを更新する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#domaアダプタを更新する) (s21)
- [Micrometerアダプタを更新する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#micrometerアダプタを更新する) (s22)
- [gsp-dba-maven-pluginを更新する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#gsp-dba-maven-pluginを更新する) (s23)
- [waitt-maven-pluginをjetty-ee10-maven-pluginに変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#waitt-maven-pluginをjetty-ee10-maven-pluginに変更する) (s24)
- [nablarch-testing-jetty6をnablarch-testing-jetty12に変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#nablarch-testing-jetty6をnablarch-testing-jetty12に変更する) (s25)
- [javax名前空間をjakarta名前空間に変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#javax名前空間をjakarta名前空間に変更する) (s26)
- [XMLスキーマ指定をJakarta EE 10のスキーマに変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#xmlスキーマ指定をjakarta-ee-10のスキーマに変更する) (s27)
- [タグライブラリのネームスペースをJakarta EE 10のネームスペースに変更する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#タグライブラリのネームスペースをjakarta-ee-10のネームスペースに変更する) (s28)
- [JSR352に準拠したバッチアプリケーションの移行手順](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/migration/migration-migration.md#jsr352に準拠したバッチアプリケーションの移行手順) (s29)
- [Nablarch5と6で名称が変更になった機能について](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/about/about-nablarch/about-nablarch-jakarta-ee.md#nablarch5と6で名称が変更になった機能について) (s2)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers both key facts from the Expected Output. Fact 1 (Jakarta EE 10 対応のアプリケーションサーバが必要) is explicitly addressed in the注意点 section mentioning 'Jakarta EE 10対応のアプリケーションサーバ（Tomcat 10以降等）が必要'. Fact 2 (Java EEの仕様名およびパッケージ名がJakarta EEのものに変更) is thoroughly covered in sections 1 through 5, explaining the javax.* → jakarta.* namespace changes across code, XML schemas, and tag libraries. All expected facts are present in the Actual Output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is completely relevant to the input, which asks about changes affecting applications when upgrading from Nablarch 5 to Nablarch 6 due to Jakarta EE 10 support. There are no irrelevant statements found in the response. |
| faithfulness | 0.99 | 0.97 | NG | The score is 0.97 because the actual output incorrectly claims that backward compatibility is not maintained at all, when the retrieval context explicitly states that class and package names have not been changed in order to maintain backward compatibility ('後方互換を維持するためにクラスやパッケージの名前は変更されていない'). |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「Jakarta EE 10対応のアプリケーションサーバで動作させる必要がある」は回答の注意点「Jakarta EE 10対応のアプリケーションサーバ（Tomcat 10以降等）が必要です」に含まれ、参照事実「Java EEの仕様名およびパッケージ名がJakarta EEのものに変更」はセクション1〜5のjavax.*→jakarta.*変更説明に含まれている |
| answer_relevancy | OK | 回答はNablarch 5→6移行時のJakarta EE 10対応で必要なアプリケーション変更（名前空間変更・依存関係更新・XMLスキーマ変更・JSPタグライブラリ変更・ツール更新・Domaアダプタ更新など）を網羅しており、すべての内容が質問に直接関連しています。的外れな情報は含まれていません。 |
| faithfulness | NG | 回答の注意点に「名前空間変更により後方互換性は一切維持されません」と記述されていますが、about-nablarch-jakarta-ee.md (s2)には「後方互換を維持するためにクラスやパッケージの名前などは変更されていない」と明示されており矛盾しています。Nablarch自身のクラス・パッケージ名は後方互換維持のために変更されていないという事実が、回答では完全に無視されています。 |

### 参照事実（expected_facts）

- Jakarta EE 10に対応しており、Jakarta EE 10対応のアプリケーションサーバで動作させる必要がある
- Java EEの仕様名およびパッケージ名がJakarta EEのものに変更されている
