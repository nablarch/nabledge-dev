# oos-impact-01 — run-1

## 質問

NablarchでOAuth2やOpenID Connectによる認証を実装したい。Nablarchにその仕組みは組み込まれているか？

## 回答

**結論**: NablarchにはOAuth2/OpenID Connectの認証機構は組み込まれていない。ただし、OIDCのIDトークンを使った認証を実装するためのビジネスサンプル（実装例）が公式に提供されている。

**根拠**:

Nablarchのウェブアプリケーション機能詳細ドキュメントには以下の記載がある：

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

つまりOAuth2/OIDCを含む認証機能はNablarchフレームワーク本体には含まれない。

その代わり、**OIDCのIDトークンを用いた認証サンプル**（`nablarch-biz-sample-all` の `nablarch-oidc` パッケージ）が提供されており、以下の構成での実装方法が示されている：

- フロントエンド（SPA・モバイルアプリ等）でIDトークンを取得し、Nablarchバックエンド（RESTfulウェブサービス）に送信
- バックエンドでIDトークンを検証し、成功時にログインセッションを確立

対応サービスとして **Amazon Cognito** と **Azure AD B2C** のサンプルが提供されている。

実装の流れは次の通り：

1. **依存ライブラリの追加**（Auth0製 `java-jwt` / `jwks-rsa`）

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

2. **コンポーネント定義**（コンポーネント設定ファイルに `CognitoIdTokenVerifier` 等を定義）

```xml
<component name="idTokenVerifier"
    class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
```

3. **業務アクションでのIDトークン検証とセッション確立**

```java
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

**注意点**:
- このサンプルは2024年9月時点の仕様に基づいており、利用するサービスの最新仕様を確認して適宜カスタマイズすること
- サービスへのアクセスに必要な情報（クライアントIDなど）は、バージョン管理システムで管理するファイルに直接記載せず、システムプロパティやOS環境変数として設定することが推奨される
- CSRF対策として、認証成功後に `SessionUtil.changeId()` と `CsrfTokenUtil.regenerateCsrfToken()` でセッションIDとCSRFトークンを変更する

参照: guide/biz-samples/biz-samples-12.json:s2, guide/biz-samples/biz-samples-12.json:s11, guide/biz-samples/biz-samples-12.json:s12, guide/biz-samples/biz-samples-12.json:s13, guide/biz-samples/biz-samples-12.json:s14, guide/biz-samples/biz-samples-12.json:s16, processing-pattern/web-application/web-application-feature-details.json:s13

## 参照ナレッジ

- [概要](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#概要) (s2)
- [依存ライブラリの追加](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#依存ライブラリの追加) (s11)
- [環境依存値の設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#環境依存値の設定) (s12)
- [コンポーネント定義の設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#コンポーネント定義の設定) (s13)
- [IDトークンの検証](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#idトークンの検証) (s14)
- [認証および成功時のログイン状態設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#認証および成功時のログイン状態設定) (s16)
- [認証](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#認証) (s13)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly states that Nablarch does not have built-in OAuth2/OpenID Connect authentication ('NablarchにはOAuth2/OpenID Connectの認証機構は組み込まれていない'), which directly covers the single expected fact. The response clearly addresses the core claim in the Expected Output. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing whether Nablarch has built-in support for OAuth2 and OpenID Connect authentication. No irrelevant statements were made! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「NablarchにはOAuth2/OpenID Connect認証の組み込み機能がないと回答している」は回答の「NablarchにはOAuth2/OpenID Connectの認証機構は組み込まれていない」に明確に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- NablarchにはOAuth2/OpenID Connect認証の組み込み機能がないと回答している
