**結論**: NablarchにはOAuth2やOpenID Connectの認証機構はフレームワークとして組み込まれていない。ただし、OIDCのIDトークンを用いた認証サンプル（`nablarch-biz-sample-all`）が提供されており、これを参考に実装できる。

**根拠**:

Nablarchの公式ドキュメントでは、ウェブアプリケーションの認証について以下のように明示されている。

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

OAuth2/OIDC専用のハンドラやアダプタは存在しない。

その代わり、**OIDCのIDトークンを用いた認証サンプル**が提供されており、以下の構成を想定している。

- バックエンド: NablarchのRESTfulウェブサービス（※サンプルはREST前提）
- フロントエンド（SPA・モバイルアプリ等）でIDトークンを取得し、バックエンドに送信する
- 対応サービス: **Amazon Cognito ユーザープール** および **Azure Active Directory B2C（ADB2C）**

実装に必要な手順の概要は以下のとおり。

**1. 依存ライブラリの追加**（Auth0の`java-jwt`と`jwks-rsa-java`を使用）

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

**2. 環境依存値の設定**（Cognitoの場合）

| 名前 | 説明 |
|---|---|
| `aws.cognito.region` | リージョンコード（例: `ap-northeast-1`） |
| `aws.cognito.userPool.id` | ユーザープールID |
| `aws.cognito.userPool.clientId` | クライアントID |

**3. コンポーネント定義（コンポーネント設定ファイル）**

```xml
<component name="idTokenVerifier"
           class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

**4. 認証業務アクションの実装例**

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

IDトークンの検証失敗時は `HttpErrorResponse(401)` を返す。

**注意点**:
- 上記サンプルはRESTfulウェブサービス（バックエンドAPI）を前提とした設計になっている。従来型のウェブアプリケーション（JSP/Thymeleaf等で画面を返す構成）に適用する場合は、アーキテクチャを調整する必要がある。
- サンプルは2024年9月時点のCognito・ADB2C仕様に基づいており、利用する際は最新の仕様を確認すること。
- 秘匿情報（クライアントIDなど）はシステムプロパティまたはOS環境変数で管理することを推奨する。

参照: guide/biz-samples/biz-samples-12.json:s2, guide/biz-samples/biz-samples-12.json:s11, guide/biz-samples/biz-samples-12.json:s12, guide/biz-samples/biz-samples-12.json:s13, guide/biz-samples/biz-samples-12.json:s14, guide/biz-samples/biz-samples-12.json:s16, processing-pattern/web-application/web-application-feature-details.json:s13