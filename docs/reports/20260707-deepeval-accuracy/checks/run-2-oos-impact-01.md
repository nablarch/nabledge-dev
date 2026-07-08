# oos-impact-01 — run-2

## 質問

NablarchでOAuth2やOpenID Connectによる認証を実装したい。Nablarchにその仕組みは組み込まれているか？

## 回答

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

## 参照ナレッジ

- [概要](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#概要) (s2)
- [依存ライブラリの追加](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#依存ライブラリの追加) (s11)
- [環境依存値の設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#環境依存値の設定) (s12)
- [コンポーネント定義の設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#コンポーネント定義の設定) (s13)
- [IDトークンの検証](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#idトークンの検証) (s14)
- [認証および成功時のログイン状態設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#認証および成功時のログイン状態設定) (s16)
- [認証](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#認証) (s13)
- [本サンプルで取り扱う範囲](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#本サンプルで取り扱う範囲) (s3)
- [認証用業務アクションのパス設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/biz-samples/biz-samples-12.md#認証用業務アクションのパス設定) (s15)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly states that Nablarch does not have built-in OAuth2 or OpenID Connect (OIDC) authentication functionality ('NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能は組み込まれていない'), which directly matches the Expected Output's single fact. The coverage is complete. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the input, directly addressing whether Nablarch has built-in support for OAuth2 and OpenID Connect authentication. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「NablarchにはOAuth2/OpenID Connect認証の組み込み機能がないと回答している」は回答の「NablarchにはOAuth2やOpenID Connect（OIDC）の認証機能は組み込まれていない」に明示されている |
| answer_relevancy | OK | 回答はNablarchにOAuth2/OIDC認証の組み込み機能がないという結論から始まり、ビジネスサンプル（nablarch-oidc）の概要・実装手順・注意点まで、すべて質問（NablarchにOAuth2/OIDC認証の仕組みが組み込まれているか）への回答として直結している。的外れな情報は含まれていない。 |
| faithfulness | OK | 回答中の「フレームワークとしては提供していない」はweb-application-feature-details.mdの記述と一致。対応サービス（Cognito/ADB2C）・依存ライブラリのバージョン（java-jwt 4.4.0、jwks-rsa 0.22.1）・コンポーネント定義XML・業務アクションのJavaコード・注意点（2024年9月時点の仕様、IDトークン取得はフロントエンド側で対象外、秘匿情報はシステムプロパティやOS環境変数で設定）は、いずれもbiz-samples-12.mdの記述と矛盾なく一致している。 |

### 参照事実（expected_facts）

- NablarchにはOAuth2/OpenID Connect認証の組み込み機能がないと回答している
