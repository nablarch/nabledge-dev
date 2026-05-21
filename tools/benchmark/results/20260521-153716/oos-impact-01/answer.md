必要なセクション情報をすべて取得できました。Step 5〜8に進みます。

---

**Step 3 選定結果（記録用）**

- **選定ページ**: `guide/biz-samples/biz-samples-12.json`（OIDCのIDトークンを用いた認証サンプル）、`about/about-nablarch/about-nablarch-policy.json`（OSSは使用しない方針）
- **除外ページ**: セキュリティチェックリスト（認証方式ではなくXSS/CSRFなど一般的な脆弱性チェック）、ウェブアプリケーション機能詳細の認証セクション（s13）は詳細な設定方法でありサンプルページで十分

**選定セクション**:
- `biz-samples-12.json:s2` high（OIDCサンプルの概要・前提構成）
- `biz-samples-12.json:s3` high（サンプルで扱う範囲）
- `biz-samples-12.json:s11` partial（依存ライブラリ）
- `biz-samples-12.json:s13` high（コンポーネント定義）
- `biz-samples-12.json:s14` high（IDトークン検証の実装）
- `biz-samples-12.json:s16` high（認証アクションの実装）
- `about-nablarch-policy.json:s6` partial（OSSは使用しない方針）

---

**Step 6 検証（verify）**

- 「NablarchにOIDC認証は標準搭載されていない」 → biz-samplesにサンプルとして提供されている点から明示的に「サンプル」として区別されており、本体機能でないことが直接読み取れる（supported）
- 「サンプルはRESTfulウェブサービスを想定」 → s2に直接記載（supported）
- 「Auth0のjava-jwtとjwks-rsa-java」 → s11に直接記載（supported）
- 「Amazon CognitoとAzure AD B2C」 → s2に直接記載（supported）
- 「認証成功後にセッションIDとCSRFトークンを変更する」 → s16に直接記載（supported）

verify_result = **PASS**

---

**最終回答**

---

**結論**: NablarchにはOAuth2/OpenID Connectの認証機能は標準で組み込まれていない。ただし、OpenID Connect（OIDC）のIDトークンを用いた認証の**ビジネスサンプル**が公式から提供されており、これを参考に実装できる。なお、このサンプルは**RESTfulウェブサービスのバックエンド**を想定した構成であり、ウェブアプリケーション（JSP/セッションベース）とは前提が異なる点に注意が必要。

---

**根拠**

Nablarchフレームワーク本体はOSSを使用しない方針（脆弱性発見時に迅速対応するため）を採っており、OIDCのような外部プロトコルへの標準対応は含まれていない。一方で、ビジネスサンプルとして `nablarch-biz-sample-all/nablarch-oidc` が提供されている。

**サンプルの想定構成**

> * Nablarchを使用したRESTfulウェブサービスのアプリケーションを、バックエンドとして稼働させる
> * IDトークンはフロントエンド（SPA、モバイルアプリ等）で取得し、バックエンドに送信する
> * 認証成功時にログインセッションを確立し、認証後はステートフルなセッション管理を行う

対応しているIDプロバイダ：
- **Amazon Cognito ユーザープール**（AWSのユーザー管理サービス）
- **Azure Active Directory B2C**（Microsoft Azureのユーザー管理サービス）

**依存ライブラリの追加**

JWTを扱うためにAuth0製ライブラリを使用する：

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

**コンポーネント定義の設定例（Amazon Cognito）**

```xml
<!-- IDトークン検証コンポーネント -->
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

**認証アクションの実装例**

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

検証失敗時はHTTPステータス401（Unauthorized）のレスポンスを返す。

---

**注意点**

- このサンプルはRESTfulウェブサービス（JAX-RS/バックエンドAPI）向けである。従来型のウェブアプリケーション（`web-application`処理方式）でOIDCを使いたい場合、サンプルをそのまま適用することはできず、構成の検討が必要になる。
- サンプルは2024年9月時点のCognito/ADB2Cの仕様に基づいており、**利用するサービスの最新仕様を必ず確認**し適宜カスタマイズすること。
- JWKSエンドポイントへのアクセスには、秘匿すべき設定値（リージョン・ユーザープールIDなど）が含まれる。これらはバージョン管理システムで管理するファイルへの記述を避け、OS環境変数やシステムプロパティで設定することが推奨される。

---

参照: `biz-samples-12.json:s2` `biz-samples-12.json:s3` `biz-samples-12.json:s11` `biz-samples-12.json:s13` `biz-samples-12.json:s14` `biz-samples-12.json:s16`

---