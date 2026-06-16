**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能は組み込まれていない。ただし、OIDCのIDトークンを使った認証を実装するためのビジネスサンプル（`nablarch-oidc`）が公式に提供されており、これをベースにして実装できる。

**根拠**:

Nablarchの認証機能について、公式ドキュメントには以下の通り明記されている：

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

その上で、OIDC認証の実装サンプル（`nablarch-biz-sample-all`）が提供されている。サンプルは以下の構成を想定している：

- Nablarchを使用したRESTfulウェブサービスをバックエンドとして稼働させる
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信する
- 認証処理は業務アクションで実装する
- 対応サービス：**Amazon Cognito ユーザープール** および **Azure Active Directory B2C (ADB2C)**

**実装手順の概要:**

1. **依存ライブラリの追加**: JWTライブラリとしてAuth0公開の `java-jwt` と `jwks-rsa-java` を使用する。

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

2. **コンポーネント定義**: IDトークン検証コンポーネントをコンポーネント設定ファイルに定義する（Cognito例）。

```xml
<component name="idTokenVerifier"
           class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

3. **IDトークン検証**: `CognitoIdTokenVerifier` がJWTの署名・有効期限・クレームを検証する。署名検証には、CognitoのJWKSエンドポイントから公開鍵をキャッシュ付きで取得する。

4. **業務アクションでの認証**: 検証成功後、セッションIDとCSRFトークンを再生成し、ユーザー情報をセッションに保持する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

**注意点**:
- サンプルは2024年9月時点のCognito/ADB2C仕様に基づいている。利用するサービスの最新仕様を確認し、適宜カスタマイズすること。
- IDトークン取得（フロントエンド側の処理）はサンプルの対象外。
- 秘匿情報（Cognito設定値等）はシステムプロパティやOS環境変数として設定し、バージョン管理対象ファイルに直接記載しないこと。

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13