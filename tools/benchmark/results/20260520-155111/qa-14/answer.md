**結論**: Nablarch 5から6へのバージョンアップ時、Jakarta EE 10対応として最も影響が大きいのは「`javax.*` 名前空間の `jakarta.*` への全面変更」と「Java EE依存ライブラリのJakarta EE版への置き換え」です。アプリケーションサーバもJakarta EE 10対応版が必要になります。

**根拠**:

Jakarta EE 9で名前空間が変更されたため、アプリケーションコードへの影響は広範囲に及びます。

**① `javax` → `jakarta` 名前空間の変更**

Javaソースコード、JSP、設定ファイル内のJava EE系`javax.*`を`jakarta.*`に置換します。

```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

コンパイルエラーが出る箇所だけでなく、文字列で指定しているものも対象です。例：`javax.servlet.forward.request_uri` → `jakarta.servlet.forward.request_uri`

**② pom.xmlの依存関係変更（主な例）**

| Java EE | Jakarta EE |
|---|---|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |

Jakarta EEのBOMを使うことで個別バージョン指定を省略できます：
```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

**③ web.xml等のXMLスキーマ変更**

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">
<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

**④ JSPのタグライブラリネームスペース変更**

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

**⑤ ウェブプロジェクト固有の変更**
- `waitt-maven-plugin` → `jetty-ee10-maven-plugin` に変更
- テストで使用する`nablarch-testing-jetty6`（または`jetty9`）→ `nablarch-testing-jetty12` に変更
  - `HttpServerFactoryJetty6` → `HttpServerFactoryJetty12` にコンポーネント設定を変更

**⑥ Jakarta Batchプロジェクト固有の変更**

JBeretおよび関連ライブラリを一括更新する必要があります（`jberet-core 2.1.4.Final`、`weld-core-impl 5.0.1.Final`等）。

**注意点**:
- `javax.crypto.SecretKeyFactory` のような標準Javaライブラリは `javax` のままで変更不要です。`javax`でgrep検索してヒットした箇所すべてが置換対象ではありません。
- 対象バージョンはNablarch 6u2が正式リリース後の最初のバージョンです。6u3以降へのバージョンアップは追加のリリースノートも確認が必要です。
- `gsp-dba-maven-plugin` を使用している場合は5.1.0以上への更新が必要です。

参照: migration-migration.json:s2, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s10, migration-migration.json:s11, migration-migration.json:s12, migration-migration.json:s13, migration-migration.json:s14, migration-migration.json:s15, migration-migration.json:s16, migration-migration.json:s17, migration-migration.json:s18, migration-migration.json:s19, migration-migration.json:s24, migration-migration.json:s25, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s29