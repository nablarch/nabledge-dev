**結論**: Nablarch 5 → 6 移行における Jakarta EE 10 対応は、アプリケーションコード・pom.xml・設定ファイルの3層にまたがる変更が必要です。後方互換性がないため、Jakarta EE 10対応のアプリケーションサーバへの移行も必須となります。

**根拠**:

### 1. 名前空間の変更（`javax.*` → `jakarta.*`）

最も広範囲に影響する変更です。Jakarta EE 9 で `javax.*` → `jakarta.*` へ名前空間が変わり、後方互換性が維持されません。

対応手順:
1. Javaソースコードの `import javax.*` がコンパイルエラーになるため `jakarta.*` に変更
2. コンパイルエラーにならない箇所（文字列リテラル、JSP、XML設定ファイル内）もGrep検索して変更
3. `javax.crypto.*` など**標準ライブラリの`javax.*`は変更不要**（Java EE仕様のもののみ変更対象）

主な対応表（一部）:

| Java EE 名前空間 | Jakarta EE 名前空間 |
|---|---|
| `javax.servlet` | `jakarta.servlet` |
| `javax.validation` | `jakarta.validation` |
| `javax.persistence` | `jakarta.persistence` |
| `javax.ws.rs` (JAX-RS) | `jakarta.ws.rs` |
| `javax.batch` | `jakarta.batch` |
| `javax.annotation` | `jakarta.annotation` |

### 2. pom.xml の依存関係変更

**Jakarta EE BOM の導入**（推奨）:
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
これにより、各依存関係のバージョンを個別指定不要になります。

**実装ライブラリの置き換え**: Bean Validation、JSTL、JAX-RS、JMSなどの実装ライブラリを Jakarta EE 対応版に差し替え。

### 3. 開発用プラグインの変更（Webアプリケーション）

| 変更前 | 変更後 |
|---|---|
| `waitt-maven-plugin` | `jetty-ee10-maven-plugin` |
| `nablarch-testing-jetty6` (NTF用) | `nablarch-testing-jetty12` |
| `HttpServerFactoryJetty6` (component定義) | `HttpServerFactoryJetty12` |

### 4. XMLスキーマの変更

`web.xml` 等:
```xml
<!-- 変更前 -->
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee" version="3.1">

<!-- 変更後 -->
<web-app xmlns="https://jakarta.ee/xml/ns/jakartaee" version="6.0">
```

### 5. JSP taglib ネームスペースの変更

```jsp
<!-- 変更前 -->
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>

<!-- 変更後 -->
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

### 6. JSR352バッチアプリケーションの追加対応

JBeret と関連ライブラリが大幅に変わります。`org.jboss.spec.javax.batch:jboss-batch-api_1.0_spec` → `jakarta.batch:jakarta.batch-api`、`weld-core` → `weld-core-impl 5.0.1.Final` など、複数の依存関係を更新する必要があります。

**注意点**:

- アプリケーションサーバ自体も **Jakarta EE 10 対応版** に更新が必要（後方互換性なし）
- Java の最低バージョンが **Java 17** に引き上げられる
- `javax.crypto.*` などの**標準ライブラリの `javax.*` は変更対象外**（Java EE仕様と区別が必要）
- Nablarch 5 のセットアップ時に Java 17 対応で追加した依存関係は、Nablarch 6 では不要になっている場合がある（`dependency:tree` で確認要）

参照: `about/migration/migration-migration.json#s2`, `about/migration/migration-migration.json#s5`, `about/migration/migration-migration.json#s9`, `about/migration/migration-migration.json#s16`, `about/migration/migration-migration.json#s24`, `about/migration/migration-migration.json#s25`, `about/migration/migration-migration.json#s26`, `about/migration/migration-migration.json#s27`, `about/migration/migration-migration.json#s28`, `about/migration/migration-migration.json#s29`