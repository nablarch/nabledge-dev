**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能はフレームワークとして組み込まれていない。ただし、OIDCのIDトークンを用いた認証の**サンプル実装**（`nablarch-biz-sample-all`）が提供されており、これをベースにプロジェクト独自に実装する形となる。

---

**根拠**:

**1. フレームワークとしての認証機能は非提供**

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

**2. OIDCサンプル（nablarch-biz-sample-all）の概要**

提供されているサンプルは以下の構成を想定している：

- Nablarchを使用したRESTfulウェブサービスのアプリケーションをバックエンドとして稼働
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信
- 認証成功時にログインセッションを確立し、認証後はステートフルなセッション管理を行う
- 認証処理は業務アクションで実装する

対応しているIDプロバイダ：
- **Amazon Cognito ユーザープール**（AWS）
- **Azure Active Directory B2C**（Azure）

**3. 依存ライブラリの追加**

JWTを処理するためにAuth0が公開している `java-jwt` と `jwks-rsa-java` を使用する：

```xml
<dependencies>
  <dependency>
    <groupId>com.auth0</groupId>
    <artifactId>java-jwt</artifactId>
    <version>4.4.0</version>
  </dependency>
  <dependency>
    <groupId>com.auth0</groupId>
    <artifactId>jwks-rsa</artifactId>
    <version>0.22.1</version>
  </dependency>
</dependencies>
```

**4. コンポーネント定義の設定（Amazon Cognitoの例）**

```xml
<!-- IDトークン検証コンポーネント -->
<component name="idTokenVerifier" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
<component name="signatureAlgorithmProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoSignatureAlgorithmProvider">
  <property name="rsaKeyProvider" ref="rsaKeyProvider" />
</component>
<component name="rsaKeyProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoRSAKeyProvider">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
</component>
```

**5. 業務アクションでの認証処理実装例**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    // IDトークンが有効であるか検証する
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 安全性向上のため、認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // IDトークンで連携された情報からユーザー情報を特定して、認証状態をセッションに保持する
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

---

**注意点**:
- サンプルは2024年9月時点のCognito/ADB2C仕様に合わせて実装されている。利用するサービスの最新仕様を確認し、適宜カスタマイズすること
- このサンプルが扱うのは**バックエンド側のIDトークン検証のみ**。フロントエンドでのIDトークン取得処理はサンプルの対象外
- 認証成功後はセッションIDとCSRFトークンを必ず再生成すること（セッション固定攻撃対策）

---

参照:
- OIDCのIDトークンを用いた認証サンプル
  .claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md
  概要
  依存ライブラリの追加
  コンポーネント定義の設定
  IDトークンの検証
  認証および成功時のログイン状態設定
- 機能詳細
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md
  認証