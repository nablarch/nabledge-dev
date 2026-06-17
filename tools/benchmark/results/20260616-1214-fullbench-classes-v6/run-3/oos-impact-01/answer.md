**結論**: NablarchはOAuth2/OIDC認証を組み込みとして持っていない。ただし、OIDCのIDトークンを検証する公式サンプル（nablarch-biz-sample-all）が提供されており、それを参考に実装できる。

**根拠**:

**Nablarchの認証に関する方針**

> 認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

（web-application-feature-details s13）

---

**OIDCサンプルの構成**

公式サンプル [nablarch-oidc](https://github.com/nablarch/nablarch-biz-sample-all/tree/main/nablarch-oidc) が提供されている。このサンプルの想定構成：

- Nablarchを**RESTfulウェブサービスのバックエンド**として稼働させる
- IDトークンは**フロントエンド（SPA、モバイルアプリ等）で取得**し、バックエンドに送信する
- 認証成功時にログインセッションを確立し、認証後はステートフルなセッション管理を行う

対応しているIDプロバイダ：
- **AWS Amazon Cognitoユーザープール**
- **Microsoft Azure ADB2C**

---

**実装手順の概要**

1. **依存ライブラリの追加** (Auth0のJWTライブラリを使用)

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

2. **環境依存値の設定**（例：Cognitoの場合）

| 名前 | 説明 |
|---|---|
| `aws.cognito.region` | リージョンコード |
| `aws.cognito.userPool.id` | ユーザープールID |
| `aws.cognito.userPool.clientId` | クライアントID |

3. **コンポーネント定義**（コンポーネント設定ファイルに登録）

```xml
<component name="idTokenVerifier"
           class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

4. **業務アクションでの認証処理**（IDトークン検証→セッション確立）

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDとCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

IDトークン検証失敗時は `HttpErrorResponse` でHTTP 401を返す。

---

**注意点**:
- このサンプルはバックエンドがRESTfulウェブサービスである構成を前提としている。通常のウェブアプリケーション（JSPベース）で使う場合は構成の見直しが必要
- サンプルのJWKSエンドポイントアクセス・署名検証ロジックは、各サービスの最新仕様に合わせてカスタマイズすること（サンプルは2024年9月時点の仕様）
- 秘匿値（クライアントIDなど）はバージョン管理対象ファイルに直書きせず、OS環境変数またはシステムプロパティで設定すること

参照: guide/biz-samples/biz-samples-12.json:s2, s11, s12, s13, s14, s16, processing-pattern/web-application/web-application-feature-details.json:s13