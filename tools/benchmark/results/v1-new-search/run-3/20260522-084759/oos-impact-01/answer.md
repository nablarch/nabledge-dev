Step 5・6・7を処理します。

**結論**: NablarchにはOAuth2/OpenID Connect認証の仕組みは**組み込まれていない**。ただし、OIDCのIDトークンを用いた認証のビジネスサンプルが提供されており、それをベースにプロジェクト側で実装する。

**根拠**:

Nablarchは「認証はプロジェクト要件により仕様が異なるため、フレームワークとして提供していない」という方針をとっている。その代わり、`nablarch-biz-sample-all` に **OIDCのIDトークンを用いた認証サンプル**（`nablarch-oidc` パッケージ）が提供されている。

#### サンプルが想定する構成

- NablarchはRESTfulウェブサービスとしてバックエンドで稼働
- フロントエンド（SPA、モバイルアプリ等）がIDトークンを取得してバックエンドに送信
- 認証成功後にステートフルなログインセッションを確立
- 対応IdP：Amazon Cognito ユーザープール、Azure Active Directory B2C

> **注意**: このサンプルはRESTfulウェブサービス向けに設計されている。ウェブアプリケーション（JSPベース）で使う場合は、業務アクションやレスポンス返却の実装をウェブアプリ向けに読み替える必要がある。

#### 実装手順の概要

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

**2. コンポーネント設定**（Cognitoの場合）

```xml
<component name="idTokenVerifier"
    class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

**3. 業務アクションでIDトークンを検証してセッションを確立**

```java
@POST
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDとCSRFトークンを更新（セキュリティ向上）
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

IDトークン検証失敗時はHTTPステータス401（Unauthorized）のレスポンスを返す。

**注意点**:
- Nablarchのプロダクションコードはフレームワーク本体では OSSを使用しない方針だが、このサンプルはビジネスサンプルとして外部JWTライブラリ（Auth0製）を使用する
- サービスはJWKSエンドポイントで署名に使う公開鍵を定期ローテーションする場合があるため、公開鍵は固定値でなくJWKSエンドポイントから動的取得する設計になっている
- 秘匿情報（ユーザープールID等）はバージョン管理ファイルに書かず、OS環境変数かシステムプロパティで設定すること

参照: `biz-samples-12.json:s2`, `biz-samples-12.json:s11`, `biz-samples-12.json:s12`, `biz-samples-12.json:s13`, `biz-samples-12.json:s14`, `biz-samples-12.json:s16`, `web-application-feature-details.json:s13`

---