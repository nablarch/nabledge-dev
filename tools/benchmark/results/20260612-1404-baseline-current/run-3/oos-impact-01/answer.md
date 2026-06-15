**結論**: NablarchにはOAuth2/OpenID Connectの認証機能は組み込まれていない。ただし、OIDCのIDトークンを用いた認証の公式実装サンプル（`nablarch-biz-sample-all`）が提供されており、これをベースに実装できる。

**根拠**:

ウェブアプリケーションの機能詳細ドキュメントに次のように明記されている。

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

一方、ビジネスサンプルとして「OIDCのIDトークンを用いた認証サンプル」が提供されており、以下の構成を想定している。

- フロントエンド（SPA・モバイルアプリ等）がIDトークンを取得してバックエンドに送信する
- バックエンド（Nablarchアプリ）でIDトークンを検証し、ログインセッションを確立する
- AWS Cognito ユーザープール、Azure ADB2C のIDトークンに対応している

**実装手順（サンプルをベースとした場合）:**

1. **依存ライブラリの追加** — Auth0の`java-jwt`と`jwks-rsa-java`をMaven依存に追加する。

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

2. **環境依存値の設定** — Cognitoの場合は以下の環境依存値を設定する。

| 名前 | 説明 |
|---|---|
| `aws.cognito.region` | リージョンコード（例：ap-northeast-1） |
| `aws.cognito.userPool.id` | ユーザープールID |
| `aws.cognito.userPool.clientId` | クライアントID |

3. **コンポーネント定義** — IDトークン検証用の3コンポーネントをコンポーネント設定ファイルに定義する。

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

4. **業務アクションでの認証処理** — IDトークンを検証し、成功時にセッションを確立する。

```java
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // ユーザー情報を特定して認証状態をセッションに保持する
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}

private DecodedJWT verifyIdToken(String idToken) {
    IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
    try {
        return idTokenVerifier.verify(idToken);
    } catch (JWTVerificationException e) {
        throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
    }
}
```

**注意点**:
- 本サンプルはRESTfulウェブサービスをバックエンドとして想定して設計されているため、ウェブアプリケーション（JSP等）で使用する場合はパス設定や呼び出し方法をプロジェクト構成に合わせて調整する必要がある
- IDトークンのフロントエンドでの取得処理はサンプルの対象外であり、別途実装が必要
- サンプルは2024年9月時点のCognito/ADB2C仕様に基づいているため、利用するサービスの最新仕様を必ず確認し適宜カスタマイズすること
- Cognitoへのアクセス情報（ユーザープールID等）はバージョン管理システムに記載せず、システムプロパティやOS環境変数として設定することが推奨されている

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s12, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13