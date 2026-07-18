### Answer

NablarchにはOAuth2/OpenID Connect（OIDC）の認証機能は組み込まれていません。ただし、**ビジネスサンプル（biz-sample）** として実装例が提供されています。

---

**提供されているOIDCサンプルの概要**

Nablarchは `nablarch-biz-sample-all` リポジトリの [`nablarch-oidc`](https://github.com/nablarch/nablarch-biz-sample-all/tree/main/nablarch-oidc) として、OIDCによる認証サンプルを提供しています。

パッケージ: `please.change.me.common.oidc.verification`

**対応しているIDプロバイダ:**
- **Amazon Cognito ユーザープール** (`...verification.cognito`)
- **Azure Active Directory B2C** (`...verification.adb2c`)

**想定アーキテクチャ:**
- バックエンド: NablarchベースのRESTfulウェブサービス
- フロントエンド（SPA・モバイルアプリ等）でIDトークンを取得し、バックエンドに送信
- バックエンドでIDトークンを検証し、認証成功後にログインセッションを確立
- 認証処理は業務アクションで実装する
- 認証後はステートフルなセッション管理を行う

※ IDトークンの取得（フロントエンド側）は本サンプルの対象外です。

---

**セキュリティ対策との関係（セキュリティチェックリストより）**

| 脆弱性 | Nablarchの対応機能 | 状況 |
|--------|-------------------|------|
| アクセス制御・認可制御の欠落（No.11） | 認可チェック機能 / Nablarch Example | △（認証はExample参照、認可は〇） |
| セッション管理の不備（No.4） | セッションストア | 〇（ログイン後の新セッション開始はExample参照） |
| クリックジャッキング（No.9） | セキュアハンドラ（X-Frame-Options: SAMEORIGIN） | 〇 |

**認証機能に関する重要な注意点:**
- Nablarch本体は認証チェック機能を提供していません。OIDCサンプルを含む実装例（Nablarch Example）を参考にプロジェクトで実装する必要があります。
- セッション管理の脆弱性対策（セッションID推測困難化・URLパラメータ禁止・secure属性等）はセッションストア機能で対応しています。ログイン成功後の新セッション開始はExampleを参考に実装してください。

---

**実装時の推奨アプローチ**

1. `nablarch-oidc` サンプルを導入プロジェクトの要件に合わせてカスタマイズする
2. ウェブアプリケーションのハンドラキューに **セッション変数保存ハンドラ**・**認可チェックハンドラ**・**セキュアハンドラ**・**CSRFトークン検証ハンドラ** を組み込む
3. 2024年9月時点の仕様に基づくサンプルのため、利用するサービス（Cognito / ADB2C）の最新仕様を確認し適宜修正する