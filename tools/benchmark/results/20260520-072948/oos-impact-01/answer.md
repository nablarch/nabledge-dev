**結論**: NablarchにはOAuth2/OpenID Connectの認証機能は組み込まれていません。認証はフレームワークとして提供しておらず、プロジェクトで実装します。ただし、OIDCのIDトークンを用いた認証を行うための**ビジネスサンプル**（`nablarch-oidc`）が公式から提供されています。

**根拠**:

ウェブアプリケーションの機能詳細ドキュメントには以下が明記されています。

> 認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

公式ビジネスサンプル（`nablarch-biz-sample-all` の `nablarch-oidc` パッケージ）では、OIDCのIDトークンを用いた認証方法が提供されています。

**サンプルの構成**:

- バックエンド（RESTfulウェブサービス）でIDトークンを検証する構成を想定
- フロントエンド（SPA・モバイルアプリ等）でIDトークンを取得し、バックエンドに送信
- 認証成功後はステートフルなセッション管理を行う
- 対応サービス: **Amazon Cognito ユーザープール** および **Azure Active Directory B2C**

**サンプルの使い方（Cognitoの場合）**:

1. JWTライブラリの依存関係を追加（Auth0の `java-jwt`, `jwks-rsa-java`）:

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

2. 環境依存値を設定（リージョン・ユーザープールID・クライアントID）
3. `CognitoIdTokenVerifier` などのコンポーネントをコンポーネント設定ファイルに定義
4. 業務アクション（`LoginAction`）でIDトークンを検証し、成功時にセッションを確立:

```java
// IDトークンを検証する
IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
DecodedJWT decodedJWT = idTokenVerifier.verify(form.getIdToken());

// セッションIDおよびCSRFトークンを変更する
SessionUtil.changeId(context);
CsrfTokenUtil.regenerateCsrfToken(context);

// 認証状態をセッションに保持する
String userId = decodedJWT.getSubject();
SessionUtil.put(context, "user.id", userId);
```

**注意点**:
- このサンプルはRESTfulウェブサービスのバックエンドを想定した構成です。ウェブアプリケーションで利用する場合は、構成を適宜調整する必要があります。
- サンプルは2024年9月時点の仕様に合わせて実装されており、利用するサービスの最新仕様を確認してカスタマイズする必要があります。
- 認証情報の保持については、`SessionUtil`を使用したセッションストアへの保存が基本です。

参照: `guide/biz-samples/biz-samples-12.json:s2`, `guide/biz-samples/biz-samples-12.json:s11`, `guide/biz-samples/biz-samples-12.json:s13`, `guide/biz-samples/biz-samples-12.json:s16`, `processing-pattern/web-application/web-application-feature-details.json:s13`