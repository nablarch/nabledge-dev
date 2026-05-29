**結論**: NablarchにはOAuth2/OpenID Connectの認証機能は組み込まれていない。ただし、OIDCのIDトークンを用いた認証を実装するためのビジネスサンプルが提供されており、それをプロジェクトに取り込んで使用できる。

**根拠**:

Nablarchの認証機能は「プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない」とされており、プロジェクトで実装する必要がある（`web-application-feature-details.json` s13）。

ただし、OIDCのIDトークンを使った認証については、以下の公式ビジネスサンプルが利用可能：

**サンプルの前提構成**:
- Nablarchのバックエンド（RESTfulウェブサービス）がIDトークンを受け取って検証する
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信する
- 対応サービス: Amazon Cognito ユーザープール、Azure Active Directory B2C

**必要な依存ライブラリ（Auth0製）**:
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

**コンポーネント定義の例（Amazon Cognito の場合）**:
```xml
<component name="idTokenVerifier" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

**業務アクションでの認証処理**:
```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

**注意点**:
- サンプルのIDトークン取得はフロントエンド側で行い、Nablarchバックエンドはトークンの検証のみを担う
- サンプルは2024年9月時点の各サービス仕様に合わせて実装されているため、利用するサービスの最新仕様を確認してカスタマイズすること
- Cognitoへのアクセス情報（リージョン、ユーザープールIDなど）には秘匿情報が含まれる場合があるため、バージョン管理対象ファイルへの直書きは避け、システムプロパティやOS環境変数で設定すること

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s12, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13

---