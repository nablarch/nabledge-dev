知識ファイルから必要な情報が揃いました。回答を生成してStep 6の検証を行います。

**Answer**

**結論**: NablarchにはOAuth2/OpenID Connect認証の組み込み機能はない。ただし、OIDCのIDトークンを用いた認証の実装サンプル（`nablarch-biz-sample-all`の`nablarch-oidc`）が公式に提供されており、これをベースにプロジェクトで実装できる。

**根拠**:

ウェブアプリケーションの機能詳細ドキュメントには「認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する」と明記されている。

**OIDCサンプルの概要**

提供サンプルでは以下の構成を想定している：

- **バックエンド**: NablarchのRESTfulウェブサービスとしてIDトークンを受け取り、検証する
- **フロントエンド**: SPA・モバイルアプリ等でIDトークンを取得し、バックエンドに送信する（フロントエンド側は本サンプルの対象外）
- **対応サービス**: Amazon Cognito ユーザープール、Azure Active Directory B2C（ADB2C）

**必要なライブラリ（pom.xml）**:

```xml
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
```

**コンポーネント定義（Cognito用）**:

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

**認証アクションの実装例**:

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

private DecodedJWT verifyIdToken(String idToken) {
    IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
    try {
        return idTokenVerifier.verify(idToken);
    } catch (JWTVerificationException e) {
        // 検証で異常を検知した場合は 401(Unauthorized) を返却する
        throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
    }
}
```

**注意点**:
- このサンプルはAmazon CognitoとAzure ADB2Cを対象としており、2024年9月時点の仕様に基づいている。利用するサービスの最新仕様を確認し、適宜カスタマイズすること。
- OAuth2の認可フロー（認可コードフロー等）はフロントエンドやAPIゲートウェイ等で処理するアーキテクチャが前提であり、Nablarch側での認可フロー全体の制御はサポートしていない。
- APIキーや秘匿情報はバージョン管理対象のファイルに記述せず、OS環境変数またはシステムプロパティとして設定すること。

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13