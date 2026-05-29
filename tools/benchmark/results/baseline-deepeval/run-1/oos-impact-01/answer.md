必要な情報が揃いました。Step 5〜8 を実行します。

---

**Step 5: 回答の生成**

以下の情報が揃いました：
- `biz-samples-12.json` s2, s3, s11, s12, s13, s14, s15, s16 — OIDCサンプルの詳細
- `web-application-feature-details.json` s13 — 認証はフレームワーク非提供

**Step 6: 検証**

クレームを確認：
- 「Nablarchは認証機能をフレームワークとして提供していない」→ s13に直接記載あり ✅
- 「OIDCサンプルが提供されている（`biz-samples`として）」→ biz-samples-12に記載あり ✅
- 「IDトークンはJWT形式」→ s11に記載あり ✅
- 「Auth0の java-jwt と jwks-rsa-java を使用」→ s11に記載あり ✅
- 「Amazon Cognito / Azure ADB2C 対応サンプル」→ s2に記載あり ✅
- 「CognitoIdTokenVerifier、CognitoSignatureAlgorithmProvider、CognitoRSAKeyProvider」→ s8, s14に記載あり ✅
- 「認証成功後に SessionUtil.changeId / CsrfTokenUtil.regenerateCsrfToken を呼ぶ」→ s16のコードに記載あり ✅
- 「失敗時は HTTP 401 を返す」→ s16に記載あり ✅

verify_result = PASS

**Step 8: 回答出力**

---

**結論**: NablarchにはOAuth2/OpenID Connectの認証機能はフレームワークとして組み込まれていません。ただし、OIDCのIDトークン（JWT）を用いた認証の実装サンプル（`nablarch-biz-sample-all`）が公式提供されており、これを参考に実装できます。

**根拠**:

Nablarch公式ドキュメントでは認証について以下のように説明しています。

> 認証については、プロジェクト要件により仕様が異なるため、フレークワークとしては提供していない。プロジェクト要件に合わせてPJで実装する。

一方、公式サンプル集（`nablarch-biz-sample-all`）に **OIDCのIDトークンを用いた認証サンプル** が提供されており、以下の構成をカバーしています。

**サンプルが想定する構成**
- Nablarch RESTfulウェブサービスをバックエンドとして稼働
- IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信
- 認証成功時にログインセッションを確立（ステートフルなセッション管理）
- 対応プロバイダ：**Amazon Cognito** および **Azure Active Directory B2C**

**依存ライブラリ（pom.xmlに追加）**
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

**コンポーネント設定（Cognito の場合）**
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

**業務アクションでの認証処理（抜粋）**
```java
@POST
@Consumes(MediaType.APPLICATION_JSON)
@Valid
public void login(ExecutionContext context, LoginRequestForm form) {
    DecodedJWT decodedJWT = verifyIdToken(form.getIdToken());

    // 認証成功後にセッションIDおよびCSRFトークンを変更する
    SessionUtil.changeId(context);
    CsrfTokenUtil.regenerateCsrfToken(context);

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
- サンプルはRESTfulウェブサービス（バックエンドAPI）向けの構成です。一般的なウェブアプリケーション（画面遷移型）でも同様の考え方で実装できますが、サンプルコードそのものはREST向けです。
- サンプルは2024年9月時点の仕様に合わせた実装のため、利用するサービスの最新仕様を確認し適宜カスタマイズが必要です。
- Nablarchは「OSSは使用しない」を基本方針としているため、OIDCプロトコルのサポート自体はフレームワーク本体に含まれません。JWTライブラリ等はアダプタ的な位置づけでプロジェクト側が追加します。

参照: guide/biz-samples/biz-samples-12.json:s2, s11, s12, s13, s14, s15, s16 / processing-pattern/web-application/web-application-feature-details.json:s13

---