セクション内容を確認しました。回答を生成します。

---

**結論**: NablarchにはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）が用意されており、ハンドラキューに追加するだけでCSRF対策が適用されます。

**根拠**:

### ハンドラキューへの追加

JSPカスタムタグを使用する標準的なウェブアプリケーションでの設定例:

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

### デフォルト動作

- `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外、`POST` `PUT` 等は検証対象
- CSRFトークンはセッションストアに格納（キー名: `nablarch_csrf-token`）
- リクエストからトークンを取得する際のパラメータ名: `csrf-token`、ヘッダ名: `X-CSRF-TOKEN`
- 検証失敗時: `400 BadRequest` を返す

### 配置制約

- **セッション変数保存ハンドラより後ろ**に配置すること（セッションストアへのトークン格納のため）
- JSPカスタムタグ使用時は**Nablarchカスタムタグ制御ハンドラより後ろ**に配置すること（hidden暗号化でCSRFトークンを画面出力するため）

### ログイン時のトークン再生成

ログイン処理でセッションIDのみ再生成する実装の場合、CSRFトークンも明示的に再生成する必要があります:

```java
CsrfTokenUtil.regenerateCsrfToken(executionContext);
```

セッションストアを破棄・再生成する実装であれば、CSRFトークンも自動的に破棄・再生成されるため不要です。

### リクエスト単体テストでの無効化

テスト時はCSRFトークン検証が失敗するため、以下の設定で無効化できます:

```xml
<!-- CSRF対策の無効化 -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

**注意点**:
- データベースを使用した二重サブミット防止機能はCSRF対策に対応していません。CSRF対策には必ずこのハンドラを使用してください
- `HttpSession`を使用した二重サブミット防止機能はCSRF対策と同等の効果がありますが、アプリケーション側で明示的に実装する必要があり対応漏れのリスクがあります。ハンドラ追加で一括対応できるこの機能の使用を推奨します

参照: `handlers-csrf-token-verification-handler.json:s3`, `handlers-csrf-token-verification-handler.json:s4`, `handlers-csrf-token-verification-handler.json:s5`, `security-check-2.チェックリスト.json:s31`

---