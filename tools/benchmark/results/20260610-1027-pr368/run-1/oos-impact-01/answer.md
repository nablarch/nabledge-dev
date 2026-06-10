**結論**: NablarchにはOAuth2/OpenID Connectの認証機能はフレームワークとして組み込まれていない。ただし、OIDCのIDトークンを用いた認証の公式サンプル（`nablarch-biz-sample-all`）が提供されており、プロジェクトで流用・カスタマイズして実装できる。

**根拠**:

Nablarch公式ドキュメントには次の通り明記されている：

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

その上で、OIDCのIDトークン認証サンプルが以下の構成で提供されている：

**対応IDプロバイダ**
- Amazon Cognito ユーザープール
- Azure Active Directory B2C (ADB2C)

**前提とする構成**
- Nablarch RESTfulウェブサービスをバックエンドとして稼働
- IDトークンはフロントエンド（SPA・モバイルアプリ等）で取得してバックエンドへ送信
- 認証成功時にログインセッションを確立（ステートフルなセッション管理）

**実装手順**

1. **依存ライブラリの追加**（Auth0製JWTライブラリを使用）

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

2. **コンポーネント設定ファイルへの定義**

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

3. **業務アクションでの認証処理**（検証成功後にセッション確立）

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDとCSRFトークンを変更（安全性向上）
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
- 本サンプルはOAuthの認可コードフローやトークン取得をNablarch側で行うものではなく、**フロントエンドで取得済みのIDトークンをバックエンドで検証する**方式である
- サンプルは2024年9月時点の仕様に基づくため、利用するサービスの最新仕様を必ず確認してカスタマイズすること
- Cognitoのリージョン・ユーザープールID・クライアントIDなどの秘匿情報は、環境変数またはシステムプロパティで設定し、バージョン管理対象ファイルへの直書きを避けること

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s12, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s15, biz-samples-12.json:s16, web-application-feature-details.json:s13