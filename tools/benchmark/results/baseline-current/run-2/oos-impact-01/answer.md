**結論**: NablarchにはOAuth2/OpenID Connectの認証機構は組み込まれていません。ただし、公式のビジネスサンプル（`nablarch-biz-sample-all`）として、OIDCのIDトークンを用いた認証のサンプル実装が提供されています。

**根拠**:

Nablarch本体にはOIDC/OAuth2の仕組みは含まれていませんが、以下の構成でOIDC認証を実現できます。

**想定アーキテクチャ**:
- バックエンド: Nablarch RESTfulウェブサービス
- IDトークン取得: フロントエンド（SPA・モバイルアプリ等）で取得し、バックエンドに送信
- 認証後はステートフルなセッション管理
- 対応サービス: AWS Amazon Cognito ユーザープール、Azure Active Directory B2C

**必要な依存ライブラリ（Auth0製JWT処理ライブラリ）**:
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

**コンポーネント設定（Cognito例）**:
```xml
<component name="idTokenVerifier" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

**認証処理（業務アクション）**:
```java
@POST
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

IDトークンの検証では、サービスが公開するJWKSエンドポイントから公開鍵を取得してRSA署名検証を行います。

**注意点**:
- サンプルは2024年9月時点の仕様に基づいており、利用するサービスの最新仕様を確認して適宜カスタマイズが必要
- フロントエンドでのIDトークン取得処理はサンプルの対象外（バックエンド側の実装のみ提供）
- 署名検証には固定値でなくJWKSエンドポイントで最新の公開鍵を取得することが推奨されている
- CSRF対策のため、認証成功後にセッションIDとCSRFトークンを再生成する実装が組み込まれている
- 検証失敗時はHTTPステータス401（Unauthorized）を返す

参照: guide/biz-samples/biz-samples-12.json#s2, guide/biz-samples/biz-samples-12.json#s11, guide/biz-samples/biz-samples-12.json#s13, guide/biz-samples/biz-samples-12.json#s14, guide/biz-samples/biz-samples-12.json#s16