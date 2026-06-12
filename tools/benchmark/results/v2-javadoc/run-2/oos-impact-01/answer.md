Step 4では既にセクション内容を取得済みです。Step 5に進んで回答を生成します。

**Step 3 選択ページ・セクション確定:**

- `guide/biz-samples/biz-samples-12.json` → 選択（OIDCのIDトークン認証サンプル、最も直接関連）
- `processing-pattern/web-application/web-application-feature-details.json` → 選択（ウェブアプリケーションの認証に関する方針が記載）
- `check/security-check/security-check-2.チェックリスト.json` → スキップ（OAuth2/OIDCの実装方法は記載なし）
- `guide/biz-samples/biz-samples-01.json` → スキップ（パスワード認証サンプルでありOAuth2/OIDCではない）

選択セクション (high): s2, s3, s11, s13, s14, s16（biz-samples-12）、s13（web-application-feature-details）  
選択セクション (partial): s1, s8, s12（biz-samples-12）

---

**結論**: NablarchにはOAuth2/OpenID Connectの認証機能は組み込まれていない。ただし、OIDCのIDトークンを用いた認証を実装するための公式サンプル（`nablarch-oidc`）が提供されており、これを参考に実装できる。

**根拠**:

Nablarchの認証は「プロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装する」とされている。

公式サンプル（`nablarch-oidc`）では以下の構成を前提にしている：

- **バックエンド**: NablarchのRESTfulウェブサービス
- **フロントエンド**: SPA・モバイルアプリ等がIDトークンを取得してバックエンドへ送信
- **対応IDプロバイダ**: AWS Cognito（`cognito`パッケージ）・Azure ADB2C（`adb2c`パッケージ）

**実装手順（Cognito使用時）:**

**1. 依存ライブラリの追加 (pom.xml)**

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

**3. 認証業務アクションの実装**

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

private DecodedJWT verifyIdToken(String idToken) {
    IdTokenVerifier idTokenVerifier = SystemRepository.get("idTokenVerifier");
    try {
        return idTokenVerifier.verify(idToken);
    } catch (JWTVerificationException e) {
        throw new HttpErrorResponse(HttpResponse.Status.UNAUTHORIZED.getStatusCode());
    }
}
```

**注意点**:
- このサンプルはバックエンドを**RESTfulウェブサービス**として構成することを想定している。JSPベースの従来型ウェブアプリケーションでは、サーバーサイドでOAuth2認可コードフローを処理する必要があり、このサンプルの直接適用はできない
- Cognito/ADB2C以外のIDプロバイダを使う場合は適宜カスタマイズが必要
- 環境依存値（リージョン、ユーザープールIDなど）にはシークレットが含まれる場合があるため、システムプロパティまたはOS環境変数で設定し、バージョン管理されるファイルへの直接記載は避けること

参照: biz-samples-12.json:s2, biz-samples-12.json:s3, biz-samples-12.json:s11, biz-samples-12.json:s13, biz-samples-12.json:s14, biz-samples-12.json:s16, web-application-feature-details.json:s13

---