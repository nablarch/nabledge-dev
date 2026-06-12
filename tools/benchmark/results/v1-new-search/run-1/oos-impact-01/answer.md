全セクションを取得しました。回答を生成します。

---

**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の仕組みは組み込まれていない。ただし、OIDCのIDトークンを用いた認証の**実装サンプル**（`nablarch-biz-sample-all`）が公式提供されており、これを参考に業務アクションとして実装できる。

**根拠**:

Nablarchの設計方針として、認証はフレームワーク側では提供しておらず、プロジェクト要件に応じてPJで実装する形になっている。

> 認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

一方、公式ビジネスサンプルとして **OIDCのIDトークンを用いた認証サンプル** が提供されており、以下の構成を実装例として参照できる。

**サンプルの前提構成**:
- NablarchをRESTfulウェブサービスのバックエンドとして使用
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信
- 認証成功時にセッションを確立（ステートフルなセッション管理）
- 認証処理は業務アクションで実装

**対応済みのIDプロバイダー**:
- AWS Amazon Cognito ユーザープール
- Microsoft Azure Active Directory B2C (ADB2C)

**実装手順の概要**:

1. JWTライブラリを依存関係に追加（Auth0の `java-jwt` と `jwks-rsa-java` を使用）

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

2. IDトークン検証コンポーネントをコンポーネント設定ファイルに定義

```xml
<component name="idTokenVerifier"
    class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

3. 業務アクションでIDトークンを検証し、成功時にセッションを確立

```java
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDとCSRFトークンを変更（セキュリティ強化）
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

**注意点**:
- サンプルはバックエンドでのIDトークン検証のみを対象としており、フロントエンドでのOAuth2認可コードフロー自体の実装は対象外
- サンプルは2024年9月時点の仕様に基づいているため、利用するサービスの最新仕様を確認してカスタマイズすること
- 秘匿情報（リージョン、クライアントIDなど）はバージョン管理システムで管理されるファイルへの直接記述を避け、OSEnvironment変数やシステムプロパティで設定すること

参照: `guide/biz-samples/biz-samples-12.json:s2`, `guide/biz-samples/biz-samples-12.json:s11`, `guide/biz-samples/biz-samples-12.json:s13`, `guide/biz-samples/biz-samples-12.json:s14`, `guide/biz-samples/biz-samples-12.json:s16`, `processing-pattern/web-application/web-application-feature-details.json:s13`

---