**結論**: NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能は標準で組み込まれていません。ただし、公式のビジネスサンプル（`nablarch-biz-sample-all`）として「OIDCのIDトークンを用いた認証サンプル」が提供されており、このサンプルを活用して実装できます。

**根拠**:

ビジネスサンプル（`biz-samples-12`）として、OpenID Connect（OIDC）のIDトークンを用いた認証実装が提供されています。サンプルの前提構成は以下のとおりです。

- NablarchをRESTfulウェブサービスのバックエンドとして稼働
- IDトークンはフロントエンド（SPA・モバイルアプリ等）で取得してバックエンドに送信
- 認証成功時にログインセッションを確立（ステートフルなセッション管理）
- 認証処理は業務アクションとして実装

対応サービス:
- Amazon Cognito ユーザープール（AWSの場合）
- Azure Active Directory B2C（Azureの場合）

実装手順の概要:

1. 依存ライブラリ追加: Auth0の `java-jwt` / `jwks-rsa-java` を使用
2. 環境依存値の設定: `aws.cognito.region`、`aws.cognito.userPool.id`、`aws.cognito.userPool.clientId` などをプロパティに設定
3. コンポーネント定義:
   - `CognitoIdTokenVerifier`: IDトークン検証
   - `CognitoSignatureAlgorithmProvider`: 署名アルゴリズム提供
   - `CognitoRSAKeyProvider`: JWKSエンドポイントからRSA公開鍵取得
4. 業務アクションでIDトークン検証後、セッションIDとCSRFトークンを再生成してセッションを確立

**注意点**:

- サンプルはバックエンド（Nablarch側）のみを対象としており、フロントエンドでのIDトークン取得処理は対象外
- 本サンプルは2024年9月時点の仕様に基づいているため、利用するサービスの最新仕様を確認して適宜カスタマイズが必要
- 秘匿情報（クライアントIDなど）はバージョン管理対象ファイルに記述せず、システムプロパティまたはOS環境変数として設定することを推奨
- CSRF対策のため `CsrfTokenUtil.regenerateCsrfToken()` の使用を想定している

参照: guide/biz-samples/biz-samples-12.json#s2, biz-samples-12.json#s11, biz-samples-12.json#s14, biz-samples-12.json#s16