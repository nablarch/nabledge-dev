**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能はフレームワークとして組み込まれていません。認証機能はプロジェクト要件により仕様が異なるためフレームワークとしては提供されておらず、プロジェクトで実装する必要があります。ただし、OIDCのIDトークンを用いた認証の実装サンプルが `nablarch-biz-sample-all` として提供されており、それを参考にして実装できます。

---

**根拠**:

ウェブアプリケーションの機能詳細ドキュメントには次の記述があります：

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

一方、OIDCのIDトークンを用いた認証サンプル（`nablarch-biz-sample-all`）が提供されており、以下の構成を想定したサンプルコードが利用できます。

**サンプルの想定構成**:
- NablarchのRESTfulウェブサービスをバックエンドとして稼働
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信
- 認証成功時にログインセッションを確立し、ステートフルなセッション管理を行う
- 認証処理は業務アクションで実装

**対応しているIDプロバイダ**（2024年9月時点）:
- AWS Amazon Cognito ユーザープール
- Microsoft Azure Active Directory B2C（ADB2C）

**依存ライブラリの追加**（Auth0製JWTライブラリを使用）:

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

**コンポーネント定義**（AWS Cognito使用時の例）:

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

**業務アクションでの認証処理**（IDトークン検証とセッション確立）:

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

    // IDトークンで連携された情報からユーザー情報を特定して、認証状態をセッションに保存する
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}

private DecodedJWT verifyIdToken(String idToken) {
    IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
    try {
        return idTokenVerifier.verify(idToken);
    } catch (JWTVerificationException e) {
        // 検証で異常を検知した場合は、ステータスコードが401(Unauthorized)のエラーレスポンスを返却する
        throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
    }
}
```

---

**注意点**:
- サンプルはOIDCのIDトークン検証を対象としており、OAuth2の認可コードフロー全体（トークン取得）はフロントエンド側で行う構成を想定しています。バックエンドが直接OAuth2フローを行う場合は別途実装が必要です。
- サンプルは2024年9月時点の各サービスの仕様に合わせて実装されているため、最新仕様を確認して適宜カスタマイズしてください。
- サンプルコードは `please.change.me` パッケージで提供されており、プロジェクト固有にカスタマイズして使用します。

参照: biz-samples-12.json:s1, biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s12, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13, libraries-session-store.json:s10

---