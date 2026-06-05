Step 5-7: 回答を生成し、検証します。

すべてのNablarch固有の主張はセクション内容に直接裏付けられています（verify_result = PASS）。

---

**結論**: NablarchにはOAuth2/OIDC認証機能はフレームワークとして組み込まれていない。ただし、OIDCのIDトークンを用いた認証実装のビジネスサンプル（biz-samples-12）が提供されており、それを参考にプロジェクト側で実装する。

**根拠**:

Nablarchの公式ドキュメントに「認証については、プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない」と明記されており、セキュリティチェックリストでも「Nablarchは認証チェックを行う機能を提供していません」と確認されている。

一方、**OIDCサンプル（biz-samples-12）**が提供されており、以下の構成を実現できる。

- 対応サービス: Amazon Cognito ユーザープール、Azure Active Directory B2C
- 想定構成: フロントエンド（SPA/モバイルアプリ）でIDトークンを取得し、NablarchのRESTfulウェブサービスバックエンドに送信して検証する

**1. 依存ライブラリの追加**

Auth0が公開しているJWTライブラリを使用する。

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

**2. コンポーネント定義の設定**

IDトークン検証コンポーネントをコンポーネント設定ファイルに定義する。

```xml
<component name="idTokenVerifier" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
<component name="signatureAlgorithmProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoSignatureAlgorithmProvider">
  <property name="rsaKeyProvider" ref="rsaKeyProvider" />
</component>
<component name="rsaKeyProvider" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoRSAKeyProvider">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
</component>
```

**3. 業務アクションでのログイン処理**

トークン検証成功後にセッションを確立する。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // ユーザー情報をセッションに保持する
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}
```

検証失敗時はHTTPステータス401（Unauthorized）のエラーレスポンスを返却する。

**4. セッションストア**

認証情報の保持にはDBストアを使用する。

**注意点**:
- 認証成功後は必ずセッションIDの変更（`SessionUtil.changeId`）とCSRFトークンの再生成（`CsrfTokenUtil.regenerateCsrfToken`）を行うこと（CSRFトークン検証ハンドラ使用時）
- サンプルは2024年9月時点のCognito・ADB2Cの仕様に基づいているため、利用する際は各サービスの最新仕様を確認してカスタマイズすること
- Cognito固有のパッケージ（`cognito`）とADB2C固有のパッケージ（`adb2c`）が分かれているため、使用するサービスに合わせて読み替えること

参照: `guide/biz-samples/biz-samples-12.json:s2`, `guide/biz-samples/biz-samples-12.json:s11`, `guide/biz-samples/biz-samples-12.json:s12`, `guide/biz-samples/biz-samples-12.json:s13`, `guide/biz-samples/biz-samples-12.json:s14`, `guide/biz-samples/biz-samples-12.json:s16`, `processing-pattern/web-application/web-application-feature-details.json:s13`, `check/security-check/security-check-2.チェックリスト.json:s11`, `component/libraries/libraries-session-store.json:s10`

---