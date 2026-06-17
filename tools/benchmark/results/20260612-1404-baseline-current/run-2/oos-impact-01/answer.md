**結論**: NablarchにはOAuth2やOpenID Connectの仕組みは組み込まれていない。ただし、OIDCのIDトークンを用いた認証を実現するためのビジネスサンプル（`nablarch-biz-sample-all/nablarch-oidc`）が提供されており、これを活用することで実装できる。

**根拠**:

Nablarchの認証機能については、ウェブアプリケーション機能詳細に以下のように明記されている。

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

その上で、OIDCを使った認証を実現するための公式サンプルとして **OIDCのIDトークンを用いた認証サンプル**（`nablarch-oidc`）が提供されている。

**サンプルが想定するアーキテクチャ:**

- Nablarchはバックエンド（RESTfulウェブサービス）として動作する
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信する
- バックエンドはIDトークンを検証し、成功時にログインセッションを確立する

**対応サービス:**
- Amazon Cognito ユーザープール
- Azure Active Directory B2C（ADB2C）

**依存ライブラリ（Auth0製のJWTライブラリを使用）:**

```xml
<dependencies>
  <!-- JWTライブラリ -->
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

**コンポーネント定義の設定例（Amazon Cognitoの場合）:**

```xml
<!-- IDトークン検証コンポーネント -->
<component name="idTokenVerifier" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
<!-- トークン署名検証用アルゴリズム提供コンポーネント -->
<component name="signatureAlgorithmProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoSignatureAlgorithmProvider">
  <property name="rsaKeyProvider" ref="rsaKeyProvider" />
</component>
<!-- トークン署名検証用RSA公開鍵提供コンポーネント -->
<component name="rsaKeyProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoRSAKeyProvider">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
</component>
```

**業務アクションでの認証処理:**

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

**注意点**:
- サンプルは2024年9月時点のCognito・ADB2Cの仕様に合わせて実装されている。利用するサービスの最新仕様を確認し、適宜カスタマイズすること
- 署名検証に使用する公開鍵はJWKSエンドポイントから動的に取得するため、固定値は使用しないこと（鍵のローテーションに対応するため）
- CSRF対策のため、`CSRFトークン検証ハンドラ`の併用を推奨する
- サービスへのアクセス情報（regionなど）はバージョン管理対象ファイルに記述せず、OS環境変数やシステムプロパティで設定すること

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13