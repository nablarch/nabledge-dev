**結論**: NablarchにはOAuth2/OpenID Connectの認証機構は組み込まれていない。ただし、OIDCのIDトークンを使った認証を実装するためのビジネスサンプル（実装例）が公式に提供されている。

**根拠**:

Nablarchのウェブアプリケーション機能詳細ドキュメントには以下の記載がある：

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

つまりOAuth2/OIDCを含む認証機能はNablarchフレームワーク本体には含まれない。

その代わり、**OIDCのIDトークンを用いた認証サンプル**（`nablarch-biz-sample-all` の `nablarch-oidc` パッケージ）が提供されており、以下の構成での実装方法が示されている：

- フロントエンド（SPA・モバイルアプリ等）でIDトークンを取得し、Nablarchバックエンド（RESTfulウェブサービス）に送信
- バックエンドでIDトークンを検証し、成功時にログインセッションを確立

対応サービスとして **Amazon Cognito** と **Azure AD B2C** のサンプルが提供されている。

実装の流れは次の通り：

1. **依存ライブラリの追加**（Auth0製 `java-jwt` / `jwks-rsa`）

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

2. **コンポーネント定義**（コンポーネント設定ファイルに `CognitoIdTokenVerifier` 等を定義）

```xml
<component name="idTokenVerifier"
    class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

3. **業務アクションでのIDトークン検証とセッション確立**

```java
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

**注意点**:
- このサンプルは2024年9月時点の仕様に基づいており、利用するサービスの最新仕様を確認して適宜カスタマイズすること
- サービスへのアクセスに必要な情報（クライアントIDなど）は、バージョン管理システムで管理するファイルに直接記載せず、システムプロパティやOS環境変数として設定することが推奨される
- CSRF対策として、認証成功後に `SessionUtil.changeId()` と `CsrfTokenUtil.regenerateCsrfToken()` でセッションIDとCSRFトークンを変更する

参照: guide/biz-samples/biz-samples-12.json:s2, guide/biz-samples/biz-samples-12.json:s11, guide/biz-samples/biz-samples-12.json:s12, guide/biz-samples/biz-samples-12.json:s13, guide/biz-samples/biz-samples-12.json:s14, guide/biz-samples/biz-samples-12.json:s16, processing-pattern/web-application/web-application-feature-details.json:s13