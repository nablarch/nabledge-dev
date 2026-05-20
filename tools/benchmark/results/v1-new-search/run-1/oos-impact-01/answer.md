**結論**: NablarchにはOAuth2/OpenID Connect認証機能は組み込まれていません。認証はフレームワークとして提供されておらず、プロジェクト要件に合わせてプロジェクト側で実装します。ただし、OIDCのIDトークンを用いた認証を実装するための**公式サンプル**が提供されており、これを活用できます。

---

**根拠**:

Nablarchの設計方針として、認証についてはプロジェクト要件により仕様が異なるため、フレームワークとして組み込みの機能は提供していません（プロジェクト要件に合わせてPJで実装します）。

その代わり、ビジネスサンプル集として **OIDCのIDトークンを用いた認証サンプル** が提供されています。

#### サンプルの概要

- パッケージ: `please.change.me.common.oidc.verification`
- 対応サービス: Amazon Cognito ユーザープール、Azure Active Directory B2C（ADB2C）
- 想定構成:
  - Nablarchをバックエンド（RESTfulウェブサービス）として稼働
  - IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得しバックエンドに送信
  - 認証成功時にセッションを確立

#### 実装ステップ

**1. 依存ライブラリの追加**（Auth0製JWTライブラリを使用）

```xml
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
```

**2. コンポーネント定義（Cognito の場合）**

```xml
<component name="idTokenVerifier"
           class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
<component name="signatureAlgorithmProvider"
           class="please.change.me.common.oidc.verification.cognito.jwt.CognitoSignatureAlgorithmProvider">
  <property name="rsaKeyProvider" ref="rsaKeyProvider" />
</component>
<component name="rsaKeyProvider"
           class="please.change.me.common.oidc.verification.cognito.jwt.CognitoRSAKeyProvider">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
</component>
```

**3. 業務アクションでの認証処理**

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDとCSRFトークンを変更（セキュリティ強化）
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}

private DecodedJWT verifyIdToken(String idToken) {
    IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
    try {
        return idTokenVerifier.verify(idToken);
    } catch (JWTVerificationException e) {
        throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
    }
}
```

**注意点**:
- サンプルは2024年9月時点のCognito/ADB2C仕様に基づいているため、利用するサービスの最新仕様を確認してカスタマイズすること
- リージョン・ユーザープールID・クライアントIDなど秘匿情報はシステムプロパティまたはOS環境変数で設定し、バージョン管理ファイルには記述しないこと
- 署名検証用の公開鍵はJWKSエンドポイントから動的に取得する設計になっており、鍵のローテーションにも対応している

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13