## Step 5: 回答生成

セクション内容を基に回答を生成します。

**結論**: NablarchにはCSRF対策専用のハンドラ `CsrfTokenVerificationHandler` があり、ハンドラキューに追加するだけでCSRFトークンの自動生成・検証が有効になります。JSPカスタムタグを使っている場合はトークンが画面に自動出力されるため、アプリケーション側での追加実装は不要です。

**根拠**: 設定例と動作仕様を含む詳細な回答を作成。

**Verify実施**: Nablarch固有のクレームを確認します。
- `CsrfTokenVerificationHandler` → s4に記載あり ✅
- `nablarch.fw.web.handler.CsrfTokenVerificationHandler` → s4に記載あり ✅
- セッション変数保存ハンドラより後ろに配置 → s3に記載あり ✅
- Nablarchカスタムタグ制御ハンドラより後ろに配置 → s3に記載あり ✅
- デフォルトはUUID v4でトークン生成 → s4に「バージョン4のUUIDを使用して」と記載あり ✅
- GET/HEAD/TRACE/OPTIONSは検証対象外 → s4に記載あり ✅
- リクエストヘッダ `X-CSRF-TOKEN` / パラメータ `csrf-token` → s4に記載あり ✅
- 検証失敗時は400を返す → s4に記載あり ✅
- `CsrfTokenUtil.regenerateCsrfToken` → s5・Javadoc s7に記載あり ✅

verify_result = PASS

---

**結論**: NablarchにはCSRF対策専用の `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）があり、ハンドラキューに追加するだけで外部サイトからの不正POSTを防ぐことができます。JSPカスタムタグを使っているウェブアプリケーションでは、CSRFトークンが画面に自動出力されるため、アプリケーションコード側での追加実装は不要です。

**根拠**:

### 基本設定

`web-component-configuration.xml`（ハンドラキューの設定ファイル）に以下を追加します。**セッション変数保存ハンドラ**と **Nablarchカスタムタグ制御ハンドラ** の後ろに配置する必要があります。

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

### デフォルトの動作

| 項目 | デフォルト動作 |
|------|--------------|
| トークン生成 | UUID v4を使用 |
| トークン格納場所 | セッションストア（キー名: `nablarch_csrf-token`） |
| 検証対象HTTPメソッド | GET/HEAD/TRACE/OPTIONS以外（POSTやPUT等） |
| トークン送信方法 | リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` |
| 検証失敗時のレスポンス | BadRequest（400） |

JSPカスタムタグを使っている場合、formタグを通じてCSRFトークンが画面に自動出力されます。

### ログイン時のトークン再生成（重要）

ログイン成功後にCSRFトークンを再生成しないと、セッション固定攻撃と組み合わせた攻撃が成立する場合があります。

- **セッションストアを破棄して再生成する実装**（推奨）: セッション破棄に合わせてCSRFトークンも自動的に破棄・再生成されるため、追加実装不要
- **セッションIDの再生成のみ行う実装**: ログイン処理の中で `CsrfTokenUtil.regenerateCsrfToken(context)` を呼び出すこと

```java
// ログインアクションの例（セッションIDのみ再生成する場合）
CsrfTokenUtil.regenerateCsrfToken(context);
```

### テスト時の注意

リクエスト単体テストではCSRFトークンの検証が失敗するため、テスト用の設定でハンドラを無効化します。

```xml
<!-- テスト設定でNopHandlerに差し替え -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

**注意点**:
- 本ハンドラはセッションストアを使用するため、セッションストアの設定が必須です
- データベースを使用した二重サブミット防止機能はCSRF対策に対応していないため、CSRF対策には必ず本ハンドラを使用してください

参照: handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6, javadoc-nablarch-common-web-csrf-CsrfTokenUtil.json:s7

---