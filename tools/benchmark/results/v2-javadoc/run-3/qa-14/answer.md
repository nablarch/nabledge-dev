Step 5で回答を生成します。

---

**結論**: Nablarch 5からNablarch 6へのバージョンアップでJakarta EE 10対応を行う場合、アプリケーションサーバの変更に加え、pom.xmlの依存関係変更・`javax`→`jakarta`の名前空間置換・XMLスキーマ変更など、アプリケーションコード・設定ファイル全体への修正が必要です。

**根拠**:

#### 1. Jakarta EE 10対応アプリケーションサーバへの移行

Jakarta EE 9で名前空間が `javax.*` から `jakarta.*` に変更されたため後方互換性が維持されない。Nablarch 6はJakarta EE 10対応のアプリケーションサーバ上での動作が必要。

#### 2. pom.xml: Java EE APIの依存関係をJakarta EEに変更

Java EEのAPI依存関係をJakarta EEのものに変更する。バージョン管理の手間を減らすため、Jakarta EE BOMの読み込みを推奨：

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

代表的な変更例（groupId/artifactId変更）：

| 変更前 | 変更後 |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

#### 3. pom.xml: Java EE仕様の実装ライブラリをJakarta EE対応版に更新

Bean Validation実装（hibernate-validator）、JSTL実装、JAX-RS実装（Jersey）、JMS実装（ActiveMQ → Artemis）など、プロジェクトで使用している実装ライブラリを各公式サイトで確認してJakarta EE対応版に置き換える。

#### 4. アプリケーションコード: `javax` 名前空間を `jakarta` 名前空間に変更

Java EEの依存関係が除去されるためコンパイルエラー箇所から着手し、その後プロジェクト全体を `javax` でGrep検索して漏れを確認する。

注意点：`javax` でヒットした箇所がすべてJava EEとは限らない（例：`javax.crypto.SecretKeyFactory` は標準ライブラリ）。付録の対応表を使って判断すること。

```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

文字列リテラルも対象。例：
- `javax.servlet.forward.request_uri` → `jakarta.servlet.forward.request_uri`

JSPや設定ファイル内の記述もコンパイルエラーにならないため、Grep検索での確認が必要。

#### 5. web.xml等のXMLスキーマをJakarta EE 10のスキーマに変更

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

#### 6. JSP: タグライブラリのネームスペースをJakarta EE 10に変更

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

#### 7. Nablarch機能の名称変更（コード変更不要）

クラス名・パッケージ名は変更されていないため、コード修正は不要。ドキュメント参照時に名称が変わっている点に注意。

| Nablarch 5までの名称 | Nablarch 6からの名称 |
|---|---|
| JAX-RS BeanValidationハンドラ | Jakarta RESTful Web Services Bean Validationハンドラ |
| JAX-RSアダプタ | Jakarta RESTful Web Servicesアダプタ |
| JSPカスタムタグ | Jakarta Server Pagesカスタムタグ |
| JSR352に準拠したバッチアプリケーション | Jakarta Batchに準拠したバッチアプリケーション |

**注意点**:
- `javax` でヒットした箇所はすべてJava EEとは限らない（`javax.crypto` などの標準ライブラリは変更不要）。付録の対応表（`javax.*` プレフィックスと仕様名の一覧）を参照して判断すること
- 移行前にNablarch 5の最新バージョン（5u25）に上げておくことが前提条件
- Nablarch 6はJava 17以上が必要

参照: migration-migration.json:s2, migration-migration.json:s5, migration-migration.json:s9, migration-migration.json:s16, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s33, about-nablarch-jakarta-ee.json:s2, releases-nablarch6u2-releasenote-6u2（5u25からの変更点）.json:s2

---