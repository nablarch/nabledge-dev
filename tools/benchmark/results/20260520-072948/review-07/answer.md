**結論**: NablarchはCSRFトークンを使った対策ハンドラ `CsrfTokenVerificationHandler` を提供しており、ハンドラ構成に追加するだけでJSP画面のCSRF対策を実装できます。JSPカスタムタグを使用している場合はCSRFトークンが画面に自動出力されるため、アプリケーションプログラマが個別に実装する必要はありません。

**根拠**:

ハンドラ構成（コンポーネント定義ファイル）に以下のように設定します。順序が重要で、`sessionStoreHandler` → `nablarchTagHandler` → `csrfTokenVerificationHandler` の順に配置する必要があります。

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

デフォルトの動作:
- CSRFトークンは `UUIDv4CsrfTokenGenerator` で生成され、セッションストアに保存される
- `GET` `HEAD` `TRACE` `OPTIONS` は検証対象外、`POST` や `PUT` 等は検証対象
- リクエストヘッダ `X-CSRF-TOKEN` またはリクエストパラメータ `csrf-token` でトークンを送信
- 検証失敗時は HTTP 400 (BadRequest) を返す

依存モジュール（`pom.xml`）:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

**注意点**:
- `CsrfTokenVerificationHandler` はセッションストアにトークンを格納するため、`sessionStoreHandler` より後ろに配置する必要があります
- JSPカスタムタグを使用する場合は `nablarchTagHandler` より後ろに配置する必要があります
- ログイン時にセッションIDのみ再生成する実装の場合は、`CsrfTokenUtil.regenerateCsrfToken` メソッドを呼び出してCSRFトークンも再生成してください（セッションストア自体を破棄・再生成する場合は不要）
- リクエスト単体テスト時はCSRF検証が失敗するため、テスト設定でハンドラを `NopHandler` に差し替えて無効化してください

参照: `component/handlers/handlers-csrf-token-verification-handler.json:s4`, `component/handlers/handlers-csrf-token-verification-handler.json:s5`