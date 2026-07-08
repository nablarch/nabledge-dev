**結論**: NablarchにはOAuth2/OpenID Connectの認証機能はフレームワークに組み込まれていない。ただし、OIDCのIDトークンを用いた認証を実装するための公式サンプル（`nablarch-biz-sample-all`）が提供されており、このサンプルを活用してバックエンドでのIDトークン検証と認証処理を実装できる。

---

**根拠**:

**フレームワークとしての認証機能の有無**

Nablarchの公式ドキュメントには以下の記述がある。

> 認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

---

**提供サンプル（nablarch-biz-sample-all）**

OIDCのIDトークン認証を実装するためのサンプルが公式に提供されている。このサンプルが想定する構成は以下の通り。

- NablarchのRESTfulウェブサービスをバックエンドとして稼働させる
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信する
- 認証成功時にログインセッションを確立し、認証後はステートフルなセッション管理を行う
- 認証処理は業務アクションで実装する

対応しているサービスは以下の2つ。

- **Amazon Cognito ユーザープール**（AWSのユーザー管理サービス）
- **Azure Active Directory B2C**（Microsoftのユーザー管理サービス）

---

**実装手順の概要**

**1. 依存ライブラリの追加**

JWTを扱うためのライブラリとして、Auth0が公開している `java-jwt` と `jwks-rsa-java` を使用する。

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

**2. コンポーネント定義の設定**

IDトークン検証コンポーネントをコンポーネント設定ファイルに定義する（Cognitoの例）。

```xml
<!-- IDトークン検証コンポーネント -->
<component name="idTokenVerifier" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
<!-- トークン署名検証用アルゴリズム提供コンポーネント -->
<component name="signatureAlgorithmProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoSignatureAlgorithmProvider">
  <property name="rsaKeyProvider" ref="rsaKeyProvider" />
</component>
<!-- トークン署名検証用RSA公開鍵提供コンポーネント -->
<component name="rsaKeyProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoRSAKeyProvider">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
</component>
```

**3. 認証処理（業務アクション）の実装**

IDトークンを検証し、成功した場合にセッションを確立する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    // IDトークンが有効であるか検証する
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 安全性向上のため、認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // IDトークンで連携された情報からユーザー情報を特定して、認証状態をセッションに保持する
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}

private DecodedJWT verifyIdToken(String idToken) {
    IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
    try {
        return idTokenVerifier.verify(idToken);
    } catch (JWTVerificationException e) {
        // 検証で異常を検知した場合は、ステータスコードが401(Unauthorized)のエラーレスポンスを返却する
        throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
    }
}
```

---

**注意点**:
- このサンプルはウェブアプリケーションではなく、**RESTfulウェブサービス**のバックエンドを想定した構成である。ウェブアプリケーション（JSPベース）に適用する場合はアーキテクチャの調整が必要になる。
- サンプルは2024年9月時点の仕様に合わせて実装されているため、利用するサービスの最新の仕様を確認し適宜カスタマイズすること。
- サービスへのアクセスに必要な認証情報（リージョンコード、クライアントIDなど）はバージョン管理システムに含めず、システムプロパティまたはOS環境変数として設定することを推奨する。

---

参照:
- OIDCのIDトークンを用いた認証サンプル
  .claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md
  概要
  本サンプルで取り扱う範囲
  依存ライブラリの追加
  コンポーネント定義の設定
  IDトークンの検証
  認証用業務アクションのパス設定
  認証および成功時のログイン状態設定
- 機能詳細
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md
  認証