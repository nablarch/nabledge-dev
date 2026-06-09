**結論**: NablarchにはOAuth2やOIDCの認証機能は組み込まれていないが、OIDCのIDトークンを検証する**公式サンプル（nablarch-oidc）** が提供されており、それを参照・カスタマイズして実装できる。

**根拠**:

Nablarchの認証機能はフレームワーク組み込みではなく、プロジェクト要件に合わせて各PJで実装する設計思想となっている。

ただし、OIDC（OpenID Connect）のIDトークンを使った認証については、`nablarch-biz-sample-all` の `nablarch-oidc` パッケージとしてサンプルが公式提供されている。

**対応しているサービス**:
- AWS Amazon Cognito ユーザープール
- Microsoft Azure Active Directory B2C (ADB2C)

**想定する構成**:
- Nablarch側はRESTfulウェブサービスとしてバックエンドで稼働
- フロントエンド（SPA、モバイルアプリ等）がIDトークンを取得し、バックエンドに送信
- 認証成功後はステートフルなセッション管理を行う

**依存ライブラリの追加** (Auth0の `java-jwt` と `jwks-rsa-java` を使用):

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

**コンポーネント定義（Cognito の例）**:

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

**業務アクションでの認証処理**:

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDとCSRFトークンを再生成（安全性向上）
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // ユーザーIDをセッションに保持
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

IDトークンの検証では、サービスのJWKSエンドポイントにアクセスしてRSA公開鍵を取得し、署名・有効期限・audience・issuer等をまとめて検証する。検証失敗時はHTTPステータス401を返す。

**注意点**:
- サンプルは2024年9月時点の仕様ベースのため、利用サービスの最新仕様を確認してカスタマイズすること
- リージョンやユーザープールIDなどの秘匿情報はシステムプロパティやOS環境変数で管理し、バージョン管理ファイルへの直書きは避けること
- ADB2C を使う場合は `adb2c` パッケージのクラスに読み替えること

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13