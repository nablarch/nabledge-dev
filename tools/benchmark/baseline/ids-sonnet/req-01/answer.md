**結論**: Nablarch にビルトインのログイン認証機能はない。ただし、公式ビジネスサンプルとしてユーザID・パスワード認証の参照実装が提供されており、それを修正して使用することが推奨されている。ログイン状態の保持にはセッションストア（DBストア）を使う。

**根拠**:

① **フレームワーク機能としては未提供**  
「認証はプロジェクト要件により仕様が異なるため、フレームワークとしては提供していない。プロジェクト要件に合わせてPJで実装すること。」  
`processing-pattern/web-application/web-application-feature_details.json:s13`

② **ビジネスサンプルで参照実装あり**  
DBに保存されたアカウント情報（ユーザID・パスワード）を使った認証サンプル実装が提供されている。パスワード暗号化にはデフォルトで PBKDF2 を使用。ただし「ログイン処理を実行する業務処理は提供しない」ため、ログイン処理そのものはプロジェクトで実装する必要がある。  
`guide/biz-samples/biz-samples-01.json:s2`

③ **SystemAccountAuthenticator の設定**  
`SystemAccountAuthenticator` を XML コンポーネント設定で登録し、`passwordEncryptor`（PBKDF2）と `dbManager` を注入する。認証失敗によるアカウントロック回数（`failedCountToLock`）も設定可能。個別アプリケーションとは別トランザクションを使うことが重要。  
`guide/biz-samples/biz-samples-01.json:s6`

④ **AuthenticationUtil による呼び出し方**  
```java
try {
    AuthenticationUtil.authenticate(userId, password);
} catch (AuthenticationFailedException e) { /* 認証失敗 */ }
  catch (UserIdLockedException e)          { /* ロック   */ }
  catch (PasswordExpiredException e)       { /* 有効期限 */ }
```
`guide/biz-samples/biz-samples-01.json:s7`

⑤ **ログイン状態の保持にはDBストアを使用**  
```java
// セッションID変更 → CSRFトークン再生成 → ユーザ情報をDBストアに保存
SessionUtil.changeId(ctx);
CsrfTokenUtil.regenerateCsrfToken(ctx);
SessionUtil.put(ctx, "user", user, "db");
```
ログアウト時は `SessionUtil.invalidate(ctx)` でセッション全体を破棄する。  
`component/libraries/libraries-session_store.json:s6`

**注意点**:
- ビジネスサンプルは「そのまま使う」ものではなく、プロジェクト要件に合わせて修正して使う前提。
- PBKDF2 のストレッチング回数・ソルトはプロジェクトごとに設定が必要（`guide/biz-samples/biz-samples-0101_PBKDF2PasswordEncryptor.json:s2`）。
- CSRFトークン検証ハンドラを使用している場合、ログイン時のセッションID変更後に `CsrfTokenUtil.regenerateCsrfToken` の呼び出しが必要。
- `SystemAccountAuthenticator` のトランザクション名（例: `"authenticator"`）は個別アプリケーション側で使用しないこと。

参照: processing-pattern/web-application/web-application-feature_details.json:s13, guide/biz-samples/biz-samples-01.json:s2, guide/biz-samples/biz-samples-01.json:s6, guide/biz-samples/biz-samples-01.json:s7, component/libraries/libraries-session_store.json:s6, guide/biz-samples/biz-samples-0101_PBKDF2PasswordEncryptor.json:s2