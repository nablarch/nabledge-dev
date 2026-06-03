全ての必要なセクションが読み込まれました。回答を生成します。

---

**結論**: NablarchにはCSRF対策機能が組み込まれており、`CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）をハンドラ構成に追加するだけで、アプリケーションプログラマが個別実装することなくCSRF対策を漏れなく適用できます。

**根拠**:

**仕組み**

本ハンドラはリクエスト処理のたびに以下を行います：
1. セッションストアからCSRFトークンを取得（なければ新規生成してセッションストアに保存）
2. POST/PUT等のHTTPメソッドを検証対象と判定（GET/HEAD/TRACE/OPTIONSは対象外）
3. リクエストのCSRFトークン（ヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token`）とセッション保存値を照合
4. 不一致の場合はBadRequest(400)を返す

JSPカスタムタグを使用している場合、CSRFトークンは画面に**自動で**出力されます。

**設定方法**

ハンドラ構成のXMLに追加するだけで有効になります：

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ（JSP使用時） -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

**ハンドラの配置順序（制約）**：
- `sessionStoreHandler`（セッション変数保存ハンドラ）の**後ろ**に配置すること
- JSPカスタムタグを使用する場合は `nablarchTagHandler`（Nablarchカスタムタグ制御ハンドラ）の**後ろ**に配置すること

**ログイン時のCSRFトークン再生成**

ログイン成功後にCSRFトークンを再生成しないと、セッション固定化攻撃と組み合わせたCSRF攻撃を受ける可能性があります。
- セッションストア自体を破棄・再生成する実装であれば、再生成は自動で行われます
- セッションIDの再生成にとどめる実装の場合は、アクション内で `CsrfTokenUtil.regenerateCsrfToken()` を呼び出してください

**注意点**:

- 本ハンドラはセッションストアを使用するため、[セッション変数保存ハンドラ]の使用が必須です
- `データベースを使用した二重サブミット防止機能`はCSRF対策に**対応していません**。データベース二重サブミット防止機能を使う場合でも、本ハンドラを別途追加してください
- リクエスト単体テスト実施時はCSRFトークン検証が失敗するため、テスト設定で本ハンドラを `NopHandler` に差し替えて無効化してください

参照: security-check-2.チェックリスト.json:s6, handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5

---