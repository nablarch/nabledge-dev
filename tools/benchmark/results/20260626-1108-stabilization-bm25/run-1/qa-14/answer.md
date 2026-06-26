**結論**: Nablarch 5から6へのバージョンアップ時、Jakarta EE 10対応として必要なアプリケーションへの変更は主に4点です。(1) Java EEの依存関係をJakarta EEに変更、(2) `javax.*` 名前空間を `jakarta.*` に置換、(3) XMLファイルのスキーマ指定をJakarta EE 10のスキーマに変更、(4) JSPのタグライブラリネームスペースを変更。また、Jakarta EE 10に対応したアプリケーションサーバへの移行が必要です。

**根拠**:

Jakarta EE 9から名前空間が `javax.*` から `jakarta.*` に変更されており、後方互換性が維持されません。そのため以下の対応がすべて必要となります。

**① Java EEの依存関係をJakarta EEに変更する（pom.xml）**

Java EE APIの`dependency`をJakarta EE対応のものに変更します。バージョン管理にはJakarta EE BOMの利用が推奨されています。

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

**② javax名前空間をjakarta名前空間に変更する（Javaソースコード・設定ファイル・JSP）**

`import`文のコンパイルエラー箇所を修正した後、プロジェクト全体を `javax` でGrep検索し、Java EEの名前空間である箇所を `jakarta` に置換します。

```java
// 修正前
import javax.validation.ConstraintValidator;

// 修正後
import jakarta.validation.ConstraintValidator;
```

なお、`javax.crypto.SecretKeyFactory` のような標準ライブラリの `javax` は変更不要です。Java EEの名前空間かどうかは、ガイド末尾の「Java EEとJakarta EEの仕様の対応表」を参照してください。

**③ XMLスキーマ指定をJakarta EE 10のスキーマに変更する（web.xml等）**

```xml
<!-- 修正前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee
         http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd"
         version="3.1">

<!-- 修正後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://jakarta.ee/xml/ns/jakartaee
                             web-app_6_0.xsd"
         version="6.0">
```

**④ タグライブラリのネームスペースをJakarta EE 10のネームスペースに変更する（JSP）**

```jsp
<%-- 修正前 --%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<%-- 修正後 --%>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

**注意点**:
- 変更対象の`dependency`は `groupId` 等から機械的に判断できないため、含まれるクラスや `artifactId` から個別に判断が必要です。
- `javax` のGrep検索は、コンパイルエラーにならないJSPや設定ファイルにも漏れが生じやすいため、プロジェクト全体を対象に実施してください。
- プロジェクトによっては不要な手順がある場合があります（例：ウェブ固有の手順はバッチプロジェクトでは不要）。

参照: migration-migration.json:s2, migration-migration.json:s5, migration-migration.json:s9, migration-migration.json:s26, migration-migration.json:s27, migration-migration.json:s28, migration-migration.json:s33, releases-nablarch6-releasenote-6.json:s2