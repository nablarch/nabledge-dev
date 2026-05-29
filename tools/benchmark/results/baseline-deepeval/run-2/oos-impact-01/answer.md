セクション読み込み完了。Step 5: 回答を生成します。

**verify結果**: 全Nablarch固有クレームはセクションコンテンツに直接裏付けされているため PASS。

---

**結論**: NablarchにはOAuth2・OpenID Connect（OIDC）の認証機構は組み込まれていません。認証はプロジェクト要件に合わせてアプリケーション側で実装する設計になっており、OIDC対応には公式の実装サンプル（`nablarch-oidc`）が提供されています。

**根拠**:

Nablarchの公式ドキュメントには以下のように明記されています：

> 認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

OIDC対応については、**OIDCのIDトークンを用いた認証サンプル**（`nablarch-biz-sample-all`）が提供されており、以下の構成を想定しています：

- フロントエンド（SPA、モバイルアプリ等）がIDトークンを取得し、Nablarchバックエンドに送信する
- バックエンドでIDトークンを検証し、成功時にログインセッションを確立する
- 認証処理は業務アクションで実装する

**サポートされているIDプロバイダ**（サンプルの対象）：
- Amazon Cognito ユーザープール
- Microsoft Azure Active Directory B2C（ADB2C）

**実装に必要な依存ライブラリの追加**（Auth0製JWTライブラリを使用）：

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

**コンポーネント定義（Cognito例）**：

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

**業務アクションでの認証処理**：

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを変更する（セキュリティ強化）
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // IDトークンからユーザーIDを取得してセッションに保存
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

IDトークンの検証は `CognitoIdTokenVerifier.verify()` が担い、署名（RSA256）・発行者・クライアントID・有効期限等を検証します。検証失敗時は HTTP 401 を返します。

**注意点**:
- サンプルは2024年9月時点の仕様に基づいています。利用するサービスの最新仕様を確認の上、適宜カスタマイズしてください。
- 接続情報（リージョン、ユーザープールID等）にはシークレットが含まれる場合があります。バージョン管理ファイルへの直接記述を避け、システムプロパティまたはOS環境変数で設定してください。
- CSRF対策として `CSRFトークン検証ハンドラ` の使用が推奨されています。

参照: `guide/biz-samples/biz-samples-12.json:s2`, `guide/biz-samples/biz-samples-12.json:s11`, `guide/biz-samples/biz-samples-12.json:s13`, `guide/biz-samples/biz-samples-12.json:s14`, `guide/biz-samples/biz-samples-12.json:s16`, `processing-pattern/web-application/web-application-feature-details.json:s13`

---