**結論**: NablarchにはCSRF対策専用のハンドラ `CsrfTokenVerificationHandler` が用意されており、ハンドラ構成に追加するだけでCSRFトークンの生成と検証が自動的に行われます。

---

**根拠**:

#### 設定方法（JSPカスタムタグを使用する場合）

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

#### ハンドラの配置順序（制約）

- **セッション変数保存ハンドラより後ろ**に配置すること（CSRFトークンをセッションストアに格納するため）
- JSPカスタムタグを使用する場合は **Nablarchカスタムタグ制御ハンドラより後ろ**に配置すること

#### デフォルトの動作

| 項目 | 内容 |
|------|------|
| トークン生成 | UUIDv4を使用（`UUIDv4CsrfTokenGenerator`） |
| トークン格納先 | セッションストア（キー名: `nablarch_csrf-token`） |
| 検証対象 | POST、PUTなど（GET/HEAD/TRACE/OPTIONSは対象外） |
| トークン受信場所 | HTTPリクエストヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token` |
| 検証失敗時 | BadRequest(400) を返す |

#### カスタマイズ例（ヘッダ名・パラメータ名の変更）

```xml
<component name="webConfig" class="nablarch.common.web.WebConfig">
  <!-- CSRFトークンをHTTPリクエストヘッダから取得する際に使用する名前 -->
  <property name="csrfTokenHeaderName" value="X-CUSTOM-CSRF-TOKEN" />
  <!-- CSRFトークンをHTTPリクエストパラメータから取得する際に使用する名前 -->
  <property name="csrfTokenParameterName" value="custom-csrf-token" />
</component>
```

#### ログイン時のCSRFトークン再生成

ログイン時にセッションIDのみ再生成する実装の場合は、アクション内で以下を呼び出してCSRFトークンも再生成すること。

```java
CsrfTokenUtil.regenerateCsrfToken(request);
```

セッションストアを破棄・再生成する実装であれば、このメソッドの呼び出しは不要です。

---

**注意点**:

- `CsrfTokenVerificationHandler` の使用には **セッションストア機能が必須**
- テスト時はハンドラを `NopHandler` に差し替えることでCSRF対策を無効化できる（テスティングフレームワーク使用時はCSRFトークン検証に失敗するため）
- データベースを使った二重サブミット防止機能はCSRF対策に対応していないため、CSRF対策には本ハンドラを使用すること

---

参照:
- CSRFトークン検証ハンドラ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-csrf-token-verification-handler.md
  制約
  CSRFトークンの生成と検証
  CSRFトークンを再生成する
- 2.チェックリスト
  .claude/skills/nabledge-6/docs/check/security-check/security-check-2.チェックリスト.md
  CSRF （クロスサイト・リクエスト・フォージェリ）