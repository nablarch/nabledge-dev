# OIDCのIDトークンを用いた認証サンプル

## 提供パッケージ

[ソースコード](https://github.com/nablarch/nablarch-biz-sample-all/tree/main/nablarch-oidc)

**パッケージ**: `please.change.me.common.oidc.verification`

## 概要

OIDCで発行されるIDトークンを用いて認証を行うサンプル。

想定構成:
1. NablarchのRESTfulウェブサービスをバックエンドとして稼働
2. IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信
3. 認証成功時にログインセッションを確立し、認証後はステートフルなセッション管理
4. 認証処理は業務アクションで実装

対応サービス別パッケージ:
- [Amazon Cognito ユーザープール](https://aws.amazon.com/jp/cognito/): `please.change.me.common.oidc.verification.cognito`
- [Azure Active Directory B2C](https://learn.microsoft.com/ja-jp/azure/active-directory-b2c/): `please.change.me.common.oidc.verification.adb2c`

adb2cパッケージ使用時は、対応するコンポーネントに読み替えること。

> **補足**: 本サンプルは2024年9月時点のユーザープール・ADB2Cの仕様に合わせて実装。利用するサービスの最新仕様を必ず確認し、適宜カスタマイズすること。

本サンプルの対象範囲はNablarchバックエンドアプリケーションのみ。フロントエンドでのIDトークン取得方法は対象外。

![処理フロー全体像](../../knowledge/about/about-nablarch/assets/about-nablarch-12/nablarch-example-oidc-scope.drawio.png)

## 構成

![クラス図](../../knowledge/about/about-nablarch/assets/about-nablarch-12/nablarch-example-oidc-class.drawio.png)

**インタフェース**:

| インタフェース名 | 概要 |
|---|---|
| `IdTokenVerifier` | IDトークンが有効であるか検証する |
| `SignatureAlgorithmProvider` | トークンの署名検証に使用するアルゴリズムを提供する |

**クラス（コンポーネント）**:

| クラス名 | 概要 |
|---|---|
| `CognitoIdTokenVerifier` | CognitoのIDトークンが有効であるか検証する |
| `CognitoSignatureAlgorithmProvider` | Cognitoのトークン署名検証に使用するアルゴリズムを提供する |
| `CognitoRSAKeyProvider` | Cognitoのトークン検証に使用するRSA公開鍵を提供する |

**クラス（業務アクション）**:

| クラス名 | 概要 |
|---|---|
| `LoginAction` | 認証処理の業務アクション |
| `LoginRequestForm` | 認証のリクエスト情報を格納するフォーム |

## 依存ライブラリの追加

IDトークンはJSON Web Tokens（JWT）形式で作成される。サンプルではAuth0が公開している `java-jwt` と `jwks-rsa-java` を使用する。

> **補足**: JWTを扱うライブラリは[OpenID Foundation](https://openid.net/developers/jwt-jws-jwe-jwk-and-jwa-implementations/)や[jwt.io](https://jwt.io/libraries)でも紹介されている。

プロジェクトの依存関係設定に以下を追加する:
```xml
<dependencies>
  ...
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
  ...
</dependencies>
```

## 環境依存値の設定

IDトークン検証コンポーネントは環境依存値をプロパティとして参照するため、以下の環境依存値を実行環境に設定する:

| 名前 | 説明 |
|---|---|
| aws.cognito.region | Cognitoを作成しているリージョンコード（例：ap-northeast-1） |
| aws.cognito.userPool.id | ユーザープールID |
| aws.cognito.userPool.clientId | ユーザープールに登録したアプリケーションのクライアントID |

環境依存値の設定方法は :ref:`repository-overwrite_environment_configuration` や :ref:`repository-overwrite_environment_configuration_by_os_env_var` を参照。

> **補足**: 秘匿すべき情報はバージョン管理システムで管理されるファイルへの記述を避け、システムプロパティまたはOS環境変数として設定する。

## コンポーネント定義の設定

IDトークン検証処理はプロパティの使用や起動時の初期化を考慮してコンポーネントとして作成する。以下をコンポーネント設定ファイルに定義する:

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

## IDトークンの検証

**`CognitoIdTokenVerifier`**: Cognitoのガイドに従ってIDトークンを検証する（有効期限の許容範囲は60秒）:
```java
JWTVerifier verifier = JWT.require(signatureAlgorithmProvider.get())
        .acceptExpiresAt(60)
        .withAudience(clientId)
        .withIssuer(createUserPoolUrl(region, userPoolId))
        .withClaim("token_use", "id")
        .build();
return verifier.verify(idToken);
```

**`CognitoSignatureAlgorithmProvider`**: RSA署名に対応するアルゴリズム情報を返す:
```java
@Override
public Algorithm get() {
    return Algorithm.RSA256(rsaKeyProvider);
}
```

**`CognitoRSAKeyProvider`**: `RSAKeyProvider`と`Initializable`を実装し、JWKSエンドポイントからRSA公開鍵を取得する:
```java
@Override
public RSAPublicKey getPublicKeyById(String keyId) {
    try {
        Jwk jwk = provider.get(keyId);
        return (RSAPublicKey) jwk.getPublicKey();
    } catch (JwkException e) {
        return null;
    }
}
```

`initialize()`でJwkProviderBuilderを構築する際の設定:
- **キャッシュ**: キーIDごとに1時間に4つまでキャッシュ（キーのローテーションを跨いだ場合でも通常使用ではキャッシュされる範囲）
- **レート制限**: JWKSエンドポイントへのアクセスは1分間に10回まで（キャッシュを考慮すると通常使用では到達しない範囲）
- **プロキシ**: プロキシは使用しない（`Proxy.NO_PROXY`）

```java
this.provider = new JwkProviderBuilder(createUserPoolUrl(region, userPoolId))
        .cached(true)
        .cached(4, 1, TimeUnit.HOURS)
        .rateLimited(true)
        .rateLimited(10, 1, TimeUnit.MINUTES)
        .proxied(Proxy.NO_PROXY)
        .build();
```

> **補足**: 署名キーはローテーションや情報漏洩等の緊急事態で変更される可能性がある。事前にキー情報が判明していても固定値を使用せず、JWKSエンドポイントから最新情報を取得すること。

## 認証用業務アクションのパス設定

認証用業務アクションのパスはJAX-RSの`@Path`アノテーションで設定する:
```java
@Path("/cognito/login")
public class LoginAction {
```

JAX-RSの`@Path`アノテーションによるマッピングの詳細は :ref:`router_adaptor_path_annotation` を参照。

## 認証および成功時のログイン状態設定

業務アクションでIDトークンを検証し、成功すればログインセッションを確立する。失敗時はHTTPステータス401のレスポンスを返却する。

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
```

IDトークン検証失敗時（`JWTVerificationException`）は`HttpErrorResponse(401)`をスロー:
```java
IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
try {
    return idTokenVerifier.verify(idToken);
} catch (JWTVerificationException e) {
    throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
}
```

> **補足**: CSRFへの対策のためCSRFトークン検証ハンドラの使用を想定。詳細は :ref:`csrf_token_verification_handler` を参照。
