必要な情報を取得しました。回答を生成します。

---

**結論**: NablarchにはOAuth2/OpenID ConnectのIDトークン検証機能は組み込まれていないが、公式の実装サンプル（`nablarch-oidc`）が提供されており、そのサンプルを使用することでAmazon Cognito や Azure AD B2C が発行するOIDC IDトークンによる認証を実装できる。

**根拠**:

本サンプルは以下の構成を前提としている：
- NablarchはバックエンドのRESTfulウェブサービスとして稼働
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信
- 認証成功時にログインセッションを確立し、以降はステートフルなセッション管理を行う
- 認証処理は業務アクションとして実装する

実装には Auth0 が公開している `java-jwt` と `jwks-rsa-java` ライブラリを使用する。依存関係の追加：

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

コンポーネント設定ファイルにIDトークン検証コンポーネントを定義する：

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

業務アクションでは、IDトークンを検証してログインセッションを確立する：

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
- NablarchのセキュリティチェックリストによるとNablarchは認証チェック機能を組み込みでは提供していない（対応状況：△）。認証はサンプルを参考にプロジェクトで実装する必要がある
- 本サンプルは Amazon Cognito ユーザープールと Azure AD B2C に対応しているが、2024年9月時点の仕様に基づいているため、利用するサービスの最新仕様を確認してカスタマイズすること
- JWKSエンドポイントから公開鍵を都度取得する方式のため、公開鍵ローテーション時にも対応できる
- CSRF対策のため、認証成功後に `SessionUtil.changeId()` と `CsrfTokenUtil.regenerateCsrfToken()` を呼び出してセッションIDとCSRFトークンを更新することが推奨されている

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, security-check-2.チェックリスト.json:s11

---