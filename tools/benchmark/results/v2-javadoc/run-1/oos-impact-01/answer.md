十分な情報が得られました。Step 5で回答を生成します。

**結論**: NablarchにはOAuth2/OpenID Connectの仕組みは組み込まれていない。ただし、**OIDCのIDトークンを用いた認証サンプル**（`nablarch-biz-sample-all`）が提供されており、これを参考に実装できる。

---

Step 6: verify実行。主要クレームを確認します。

- 「NablarchにはOAuth2/OIDCの仕組みは組み込まれていない」→ `web-application-feature-details.json:s13` に「認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない」と明記。✅ supported
- 「OIDCのIDトークンを用いた認証サンプルが提供されている」→ `biz-samples-12.json:s1/s2` に明記。✅ supported
- 「Auth0の`java-jwt`と`jwks-rsa-java`を使用」→ `s11`に明記。✅ supported
- 「AWS Cognito, Azure ADB2Cをサポート」→ `s2`に明記。✅ supported
- 「サンプルはRESTfulウェブサービスのバックエンドを想定」→ `s2`に明記。✅ supported
- 「`CognitoIdTokenVerifier`でJWTを検証し、検証失敗時に401を返す」→ `s14`, `s16`に明記。✅ supported
- 「`JwkProviderBuilder`でJWKSエンドポイントから公開鍵を取得する」→ `s14`に明記。✅ supported

verify_result = PASS

---

**最終回答を出力します。**

---

**結論**: NablarchにはOAuth2/OpenID Connectの認証機能は**組み込まれていない**。認証はプロジェクト要件により仕様が異なるため、フレームワークとしては提供されていない。ただし、**OIDCのIDトークンを用いた認証サンプル**（`nablarch-biz-sample-all`）が公式に提供されており、これを参考に実装できる。

**根拠**:

### サンプルの概要

サンプルは `nablarch-biz-sample-all` リポジトリの `nablarch-oidc` パッケージで提供される。以下の構成を想定している。

- **バックエンド**: NablarchのRESTfulウェブサービス（注：サンプルはRESTfulウェブサービスを対象としており、ウェブアプリケーションに適用する場合は適宜読み替えが必要）
- **フロントエンド**: SPA・モバイルアプリ等でIDトークンを取得し、バックエンドに送信する
- 認証成功後はセッションでステートフルに管理する

対応するOIDCサービス:
- **AWS Amazon Cognito ユーザープール** (`cognito` パッケージ)
- **Azure Active Directory B2C** (`adb2c` パッケージ)

### 依存ライブラリの追加

IDトークン（JWT形式）の処理にAuth0製ライブラリを使用する。

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

### コンポーネント定義

```xml
<!-- IDトークン検証コンポーネント -->
<component name="idTokenVerifier" class="please.change.me.common.oidc.verification.cognito.jwt.CognitoIdTokenVerifier">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
  <property name="clientId" value="${aws.cognito.userPool.clientId}" />
  <property name="signatureAlgorithmProvider" ref="signatureAlgorithmProvider" />
</component>
<component name="signatureAlgorithmProvider" class="...CognitoSignatureAlgorithmProvider">
  <property name="rsaKeyProvider" ref="rsaKeyProvider" />
</component>
<component name="rsaKeyProvider" class="...CognitoRSAKeyProvider">
  <property name="region" value="${aws.cognito.region}" />
  <property name="userPoolId" value="${aws.cognito.userPool.id}" />
</component>
```

### 認証処理（業務アクション）

IDトークンを検証し、失敗時はHTTPステータス401を返す。

```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを再生成
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

    // 認証状態をセッションに保持
    String userId = decodedJWT.getSubject();
    SessionUtil.put(context, "user.id", userId);
}

private DecodedJWT verifyIdToken(String idToken) {
    IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
    try {
        return idTokenVerifier.verify(idToken);
    } catch (JWTVerificationException e) {
        // 検証失敗時は401を返す
        throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
    }
}
```

**注意点**:
- このサンプルは**RESTfulウェブサービス**向けに設計されている。ウェブアプリケーション（JSPベース等）で使用する場合は、業務アクションの実装方法を処理方式に合わせて読み替えること。
- AWS CognitoやAzure ADB2C以外のOIDCプロバイダを使用する場合は、`IdTokenVerifier`インタフェースを実装したカスタムコンポーネントを作成する必要がある。
- 秘匿情報（リージョン、クライアントIDなど）はシステムプロパティまたはOS環境変数で設定し、バージョン管理対象のファイルに直接記述しないこと。
- 公開鍵は固定値でなくJWKSエンドポイントから取得すること（キーのローテーションに対応するため）。

参照: biz-samples-12.json:s2, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13

---