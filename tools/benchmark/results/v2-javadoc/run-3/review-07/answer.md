全セクションを読み込みました。回答を生成します。

---

**結論**: NablarchにはCSRF対策として `CsrfTokenVerificationHandler`（CSRFトークン検証ハンドラ）が用意されており、ハンドラキューに追加するだけでPOST等のリクエストに対してCSRFトークンの生成・検証が自動的に行われます。

**根拠**:

### 仕組み

`CsrfTokenVerificationHandler` は以下の流れで動作します。

1. セッションストアからCSRFトークンを取得（なければ生成して保存）
2. HTTPメソッドが `GET` / `HEAD` / `TRACE` / `OPTIONS` → 検証対象外
3. `POST` / `PUT` 等 → リクエストヘッダ `X-CSRF-TOKEN` またはパラメータ `csrf-token` からトークンを取得して検証
4. 検証失敗 → `400 BadRequest` を返す

JSPカスタムタグを使っている場合は、CSRFトークンがhiddenパラメータとして自動的に画面に埋め込まれるため、アプリケーション側の追加実装は不要です。

### 設定方法

コンポーネント設定ファイルのハンドラキューに以下を追加します（順序に注意）。

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- 他のハンドラは省略 -->

      <!-- セッションストアハンドラ（先に配置する） -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ（JSP使用時は先に配置する） -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

**注意点**:

- **セッションストア必須**: CSRFトークンはセッションストアに保存されるため、`SessionStoreHandler` より後ろに配置すること
- **JSP使用時**: `NablarchTagHandler`（Nablarchカスタムタグ制御ハンドラ）より後ろに配置すること
- **ログイン時のトークン再生成**: ログイン処理でセッションIDのみを再生成（セッションストア自体を破棄しない）場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成すること。セッションストアごと破棄して再生成する場合は不要
- **テスト時**: リクエスト単体テストではCSRFトークン検証が失敗するため、テスト設定で `NopHandler` に差し替えて無効化すること

```xml
<!-- テスト用設定でCSRF対策を無効化 -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

参照: handlers-csrf-token-verification-handler.json:s3, handlers-csrf-token-verification-handler.json:s4, handlers-csrf-token-verification-handler.json:s5, security-check-2.チェックリスト.json:s6

---