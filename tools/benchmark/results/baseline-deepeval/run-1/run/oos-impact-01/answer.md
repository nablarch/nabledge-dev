**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能は組み込まれていない。ただし、OIDCのIDトークンを用いた認証を実装するためのビジネスサンプル（`nablarch-biz-sample-all`）が提供されており、これを参考に実装できる。

---

**根拠**:

Nablarchの公式ドキュメントには次のとおり明記されている。

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

一方、**OIDCのIDトークンを用いた認証サンプル**（`nablarch-oidc`）が提供されており、以下の構成を想定している。

- Nablarchを使ったRESTfulウェブサービスをバックエンドとして稼働
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得してバックエンドに送信
- 対応サービス: **Amazon Cognito ユーザープール** と **Azure Active Directory B2C**

**実装手順の概要**:

1. **依存ライブラリの追加**: Auth0の`java-jwt`と`jwks-rsa-java`を使用する。

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

2. **コンポーネント定義の設定**: IDトークン検証コンポーネント群をコンポーネント設定ファイルに定義する。

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

3. **業務アクションでの認証処理**: IDトークンを検証し、成功時にログインセッションを確立する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // ユーザー情報を特定して認証状態をセッションに保持する
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

---

**注意点**:
- 本サンプルはIDトークンの検証（バックエンド側）のみを対象とし、フロントエンドでのIDトークン取得方法は対象外。
- Cognito・ADB2C以外のIDプロバイダを使う場合は、対応する検証コンポーネントを自プロジェクトで実装する必要がある。
- Cognitoの環境依存値（リージョン、ユーザープールID、クライアントID）はバージョン管理対象外のシステムプロパティやOS環境変数で設定することが推奨される。

参照: `guide/biz-samples/biz-samples-12.json:s2`, `s11`, `s12`, `s13`, `s14`, `s16`, `processing-pattern/web-application/web-application-feature-details.json:s13`

---