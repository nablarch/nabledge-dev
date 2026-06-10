**結論**: Nablarch 5からNablarch 6へのバージョンアップ時、Jakarta EE 10対応としてアプリケーションに影響する主な変更は「①`javax.*`名前空間を`jakarta.*`に変更」「②Java EEのdependencyをJakarta EE版に変更」「③XMLスキーマ・タグライブラリのネームスペース変更」の3点です。加えてJava 17以上への移行と、アプリケーションサーバのJakarta EE 10対応が必要です。

**根拠**:

**移行の2大作業**（`migration-migration.json:s5`）

1. **Nablarchのバージョンアップ** — `pom.xml`のBOMバージョンを`6u2`に変更する

```xml
<dependency>
  <groupId>com.nablarch.profile</groupId>
  <artifactId>nablarch-bom</artifactId>
  <version>6u2</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

2. **Jakarta EE対応** — 以下の変更が必要

---

**① Java EEのdependencyをJakarta EEに変更**（`migration-migration.json:s9`）

Jakarta EEが提供するBOMを読み込む方法が推奨：

```xml
<dependency>
  <groupId>jakarta.platform</groupId>
  <artifactId>jakarta.jakartaee-bom</artifactId>
  <version>10.0.0</version>
  <type>pom</type>
  <scope>import</scope>
</dependency>
```

代表的な個別変更例：

| 変更前 | 変更後 |
|--------|--------|
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` |
| `javax.servlet.jsp:javax.servlet.jsp-api` | `jakarta.servlet.jsp:jakarta.servlet.jsp-api` |
| `javax.servlet.jsp.jstl:javax.servlet.jsp.jstl-api` | `jakarta.servlet.jsp.jstl:jakarta.servlet.jsp.jstl-api` |
| `javax.ws.rs:javax.ws.rs-api` | `jakarta.ws.rs:jakarta.ws.rs-api` |
| `javax.annotation:javax.annotation-api` | `jakarta.annotation:jakarta.annotation-api` |
| `org.hibernate:hibernate-validator:5.3.6.Final` | `org.hibernate.validator:hibernate-validator:8.0.0.Final` |

---

**② `javax`名前空間を`jakarta`名前空間に変更**（`migration-migration.json:s26`）

Jakarta EE 9で名前空間が`javax.*`から`jakarta.*`に変更された。対応手順：

1. コンパイルエラーになる`javax`の`import`文を`jakarta`に変更
2. プロジェクト全体を`javax`でGrep検索し、コンパイルエラーにならない箇所も調査
3. 付録の「Java EEとJakarta EEの仕様の対応表」でJava EEの名前空間かどうか判定
4. Java EEの名前空間と判断できた場合に`jakarta`に置換

例：
```java
// 修正前
import javax.validation.ConstraintValidator;
// 修正後
import jakarta.validation.ConstraintValidator;
```

※`javax.crypto.SecretKeyFactory`のような標準ライブラリの`javax`は置換不要。

---

**③ XMLスキーマ・タグライブラリのネームスペース変更**

`web.xml`等のXMLスキーマ（`migration-migration.json:s27`）：

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">
<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

JSPのタグライブラリ（`migration-migration.json:s28`）：

```jsp
<!-- 修正前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!-- 修正後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

---

**注意点**:

- **Java 17以上が必須**：Nablarch 6のモジュールはJava 17でコンパイルされているため、実行環境をJava 17以上にする必要がある（`migration-migration.json:s3`）
- **アプリケーションサーバの変更が必要**：Jakarta EE 10に対応しているアプリケーションサーバで動作させる必要がある（`releases-nablarch6-releasenote-6.json:s2`）
- **前提条件**：まずNablarch 5の最新版へのバージョンアップを済ませてから移行すること（`migration-migration.json:s4`）
- **6/6u1は先行リリース**：ここで説明する手順はNablarch 5最新版からNablarch **6u2**へのバージョンアップを前提としている。6u3以降へのバージョンアップは追加手順が必要な場合があるため、各リリースノートを順に参照すること
- ウェブプロジェクト固有の追加対応として `waitt-maven-plugin` → `jetty-ee10-maven-plugin`の変更、`nablarch-testing-jetty6` → `nablarch-testing-jetty12`の変更も必要

参照: migration-migration.json:s2, migration-migration.json:s3, migration-migration.json:s5, migration-migration.json:s7, migration-migration.json:s9, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, releases/releases/releases-nablarch6-releasenote-6.json:s2, releases/releases/releases-nablarch6-releasenote-6.json:s3