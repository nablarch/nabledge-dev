**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能は組み込まれていません。ただし、公式のビジネスサンプル（`nablarch-oidc`）として、OIDCのIDトークンを用いた認証の参照実装が提供されています。

**根拠**:

Nablarch公式ビジネスサンプル `nablarch-oidc` では以下の構成でOIDC認証を実装します。

**対応IDプロバイダー**
- Amazon Cognito ユーザープール（パッケージ: `cognito`）
- Azure Active Directory B2C（パッケージ: `adb2c`）

**想定アーキテクチャ**
- フロントエンド（SPA・モバイルアプリ等）でIDトークンを取得し、Nablarchバックエンド（RESTfulウェブサービス）に送信
- バックエンドでIDトークンを検証し、認証成功後にステートフルなセッションを確立

**依存ライブラリ（pom.xml）**
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

**コンポーネント定義（XML）**
```xml
<component name="idTokenVerifier"
           class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

**IDトークン検証ロジック（Java）**
```java
// CognitoIdTokenVerifier.verify()
JWTVerifier verifier = JWT.require(signatureAlgorithmProvider.get())
    .acceptExpiresAt(60)
    .withAudience(clientId)
    .withIssuer(createUserPoolUrl(region, userPoolId))
    .withClaim("token_use", "id")
    .build();
return verifier.verify(idToken);
```

**業務アクション（LoginAction）**
```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // セッションIDおよびCSRFトークンを変更（セキュリティ対策）
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // ユーザー情報をセッションに保持
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

検証失敗時は `HttpErrorResponse` でHTTPステータス401を返します。

**注意点**:
- このサンプルはNablarch本体ではなく **ビジネスサンプル** として提供されます。プロジェクトに取り込んでカスタマイズして使用してください
- フロントエンドでのIDトークン取得処理（OAuthフロー）はサンプルの対象外です
- サンプルは2024年9月時点のCognito・ADB2C仕様に合わせて実装されているため、利用するサービスの最新仕様を確認し適宜カスタマイズしてください
- JWKSエンドポイントへのアクセスはキャッシュ（1時間・4件まで）とレートリミット（1分・10回まで）が設定されています
- Cognito以外のOIDCプロバイダーへの対応は、`IdTokenVerifier` / `SignatureAlgorithmProvider` インタフェースを実装することで拡張可能です

参照: `guide/biz-samples/biz-samples-12.json#s2`, `guide/biz-samples/biz-samples-12.json#s11`, `guide/biz-samples/biz-samples-12.json#s13`, `guide/biz-samples/biz-samples-12.json#s14`, `guide/biz-samples/biz-samples-12.json#s16`