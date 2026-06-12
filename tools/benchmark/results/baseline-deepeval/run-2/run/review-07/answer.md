**結論**: NablarchにはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）が用意されており、ハンドラ構成に追加するだけで漏れなくCSRF対策を実施できます。アプリケーション側に個別実装は不要です。

---

**根拠**:

### 1. ハンドラ構成への追加（Jakarta Server Pagesカスタムタグを使用する場合）

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

### 2. デフォルト動作

- **トークン生成**: UUIDv4で生成し、セッションストアへ保存（変数名: `nablarch_csrf-token`）
- **検証対象**: `GET` `HEAD` `TRACE` `OPTIONS` はチェック対象外（POST、PUTなどが検証対象）
- **トークン送信方法**: HTTPリクエストヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token`
- **検証失敗時**: BadRequest（400）を返す
- **JSPカスタムタグ使用時**: CSRFトークンが画面に自動出力される

### 3. ログイン時のトークン再生成

ログイン後にCSRFトークンを再生成しないと、悪意のある第三者がトークンを仕込んだ罠ページを用意できてしまいます。

- **セッションストアごと破棄・再生成する実装**: CSRFトークンも自動的に無効化されるため、追加対応不要
- **セッションIDのみ再生成する実装**: アクション等のリクエスト処理中に `CsrfTokenUtil.regenerateCsrfToken` を呼び出すこと

---

**注意点**:

1. **ハンドラの配置順序**: セッション変数保存ハンドラおよびNablarchカスタムタグ制御ハンドラより**後ろ**に配置する必要があります（CSRFトークンをセッションストアに格納するため）。
2. **リクエスト単体テスト時**: 正しい画面遷移を経由しないためCSRFトークン検証が失敗します。テスト設定でコンポーネント名を合わせて `NopHandler` に差し替えて無効化してください：

```xml
<!-- CSRF対策の無効化（テスト用設定） -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

3. **二重サブミット防止機能との違い**: NablarchのHttpSessionを使った二重サブミット防止機能でもCSRF対策効果は得られますが、アプリケーションプログラマが明示的に実装する必要があり対策漏れが生じる可能性があります。CSRF対策には`CsrfTokenVerificationHandler`の使用を推奨します。

参照: `handlers-csrf-token-verification-handler.json:s4`, `handlers-csrf-token-verification-handler.json:s5`, `handlers-csrf-token-verification-handler.json:s3`, `security-check-2.チェックリスト.json:s6`

---