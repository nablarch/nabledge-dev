**結論**: NablarchにはOAuth2・OpenID Connect（OIDC）の認証機能はフレームワーク組み込みでは提供されていません。ただし、OIDCのIDトークン（JWT）を用いた認証を実装するための**ビジネスサンプル（biz-samples-12）**が公式提供されており、Amazon Cognito・Azure AD B2Cに対応した実装例を参照できます。

---

**根拠**:

Nablarchの公式ドキュメントには次の記述があります。

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。
> （web-application-feature-details.json s13）

> Nablarchは認証チェックを行う機能を提供していません。NablarchのExampleとして提供している実装例を参考に認証機能を実装してください。
> （security-check-2.チェックリスト.json s11）

**ビジネスサンプル（biz-samples-12）の概要**:

本サンプルは以下の構成を想定しています。

- Nablarch RESTfulウェブサービスをバックエンドとして稼働
- フロントエンド（SPA、モバイルアプリ等）でIDトークンを取得しバックエンドに送信
- バックエンドでJWTを検証し、成功時にステートフルなセッションを確立

対応しているサービス：
- **Amazon Cognito ユーザープール**
- **Azure Active Directory B2C**

**必要な依存関係**:

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

**コンポーネント定義**（Cognito の例）:

```xml
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

**ログインアクションの実装例**:

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    // IDトークンが有効であるか検証する
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // ユーザー情報をセッションに保持する
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

---

**注意点**:

- サンプルが対象とするのは**バックエンドでのIDトークン検証のみ**です。フロントエンドでのIDトークン取得はサンプルの対象外であり、プロジェクトで別途実装が必要です。
- サンプルは2024年9月時点のCognito・ADB2Cの仕様に合わせた実装です。利用するサービスの最新仕様を確認し、適宜カスタマイズしてください。
- Cognitoのリージョン・ユーザープールID・クライアントIDなど秘匿情報は、バージョン管理対象ファイルに直接記述せず、システムプロパティやOS環境変数として設定することが推奨されています。

---

参照: biz-samples-12.json:s2, biz-samples-12.json:s3, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s16, security-check-2.チェックリスト.json:s11, web-application-feature-details.json:s13

---