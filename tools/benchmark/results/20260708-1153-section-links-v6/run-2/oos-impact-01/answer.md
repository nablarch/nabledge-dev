**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能はフレームワークとして組み込まれていない。ただし、OIDCのIDトークンを用いた認証の公式サンプル（biz-sample）が提供されており、これを参考に実装できる。なお、このサンプルはNablarchのRESTfulウェブサービスをバックエンドとする構成を想定している。

---

**根拠**:

**フレームワーク非提供の明示**（ウェブアプリケーション 機能詳細 > 認証より）:
> 認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

**OIDCサンプルの概要**（OIDCのIDトークンを用いた認証サンプル > 概要より）:
- フロントエンド（SPA、モバイルアプリ等）でIDトークンを取得し、バックエンドへ送信
- バックエンドでIDトークンを検証し、ログインセッションを確立
- 対応IDプロバイダ: Amazon Cognito ユーザープール / Azure Active Directory B2C

**ライブラリの追加**（依存ライブラリの追加より）:
Auth0が公開するJWTライブラリを使用する:
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

**コンポーネント定義**（コンポーネント定義の設定より）:
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

**業務アクションでの認証実装**（認証および成功時のログイン状態設定より）:
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

    // ユーザー情報を特定して認証状態をセッションに保持する
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```
IDトークン検証失敗時は `HttpErrorResponse(401)` を返却する。

---

**注意点**:
- このサンプルはRESTfulウェブサービスのバックエンドを想定した構成のため、従来のウェブアプリケーション（サーバーサイドレンダリング）に適用する場合はアーキテクチャを調整する必要がある
- IDトークンの取得（フロントエンド側）はサンプルの対象外
- サンプルは2024年9月時点のCognito・ADB2Cの仕様に基づいており、最新仕様を確認して適宜カスタマイズすること
- OIDCに対応する業務アクションのパスは `@Path` アノテーションで設定する（JAX-RSのPathアノテーションによるマッピングを使用）

参照:
- OIDCのIDトークンを用いた認証サンプル
  .claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md
  概要
  本サンプルで取り扱う範囲
  依存ライブラリの追加
  コンポーネント定義の設定
  IDトークンの検証
  認証および成功時のログイン状態設定
- 機能詳細
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md
  認証