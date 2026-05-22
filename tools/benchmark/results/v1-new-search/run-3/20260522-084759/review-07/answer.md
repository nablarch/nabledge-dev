Step 5〜7: 回答を生成し、検証します。

---

**結論**: NablarchにはCSRFトークン検証ハンドラ（`CsrfTokenVerificationHandler`）が用意されており、ハンドラ構成に追加するだけでCSRF対策が自動的に適用される。二重サブミット防止機能でも同等の効果は得られるが、漏れなくチェックできるCSRFトークン検証ハンドラの使用が推奨される。

---

**根拠**:

### 依存モジュールの追加

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

### ハンドラ構成への追加（JSPカスタムタグを使用する場合）

```xml
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

| 項目 | デフォルト動作 |
|------|-------------|
| トークン生成 | バージョン4のUUIDで生成（`UUIDv4CsrfTokenGenerator`） |
| 検証対象外メソッド | `GET` `HEAD` `TRACE` `OPTIONS` |
| トークンの受け取り方法 | HTTPリクエストヘッダ `X-CSRF-TOKEN` または HTTPパラメータ `csrf-token` |
| 検証失敗時 | `400 BadRequest` を返す |

---

**注意点**:

**1. ハンドラの配置順序**

- `SessionStoreHandler`（セッション変数保存ハンドラ）**より後ろ**に配置すること（CSRFトークンをセッションストアに格納するため）
- JSPカスタムタグを使用する場合は `NablarchTagHandler`（Nablarchカスタムタグ制御ハンドラ）**より後ろ**に配置すること

**2. ログイン時のトークン再生成**

ログイン成功時にCSRFトークンを再生成しないと、セッション固定攻撃と組み合わせた攻撃が成立する可能性がある。ログイン処理のアクション内で以下を呼び出すこと：

```java
CsrfTokenUtil.regenerateCsrfToken(request);
```

なお、ログイン時にセッションストアを破棄・再生成する実装であれば、このメソッドの呼び出しは不要（セッションストア破棄時にCSRFトークンも破棄されるため）。

**3. リクエスト単体テスト時の無効化**

テスティングフレームワークを使ったリクエスト単体テストでは、正しい画面遷移を経由しないためCSRFトークン検証が失敗する。テスト設定でハンドラを `NopHandler` に差し替えること：

```xml
<!-- テスト設定でCSRF対策を無効化 -->
<component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
```

---

参照: `handlers-csrf-token-verification-handler.json:s4`, `handlers-csrf-token-verification-handler.json:s3`, `security-check-2.チェックリスト.json:s31`, `handlers-csrf-token-verification-handler.json:s5`, `handlers-csrf-token-verification-handler.json:s2`

---