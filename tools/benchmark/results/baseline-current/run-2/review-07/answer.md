**結論**: NablarchにはCSRF対策用の専用ハンドラ（`CsrfTokenVerificationHandler`）があります。ハンドラ構成に追加するだけで、アプリケーションコードの変更なしにCSRF対策が自動で機能します。

**根拠**:

**仕組み**

`CsrfTokenVerificationHandler` がリクエスト処理で以下を自動的に行います：

1. セッションストアからCSRFトークンを取得（なければ生成して保存）
2. HTTPリクエストが検証対象かを判定（`GET` / `HEAD` / `TRACE` / `OPTIONS` は対象外、`POST` / `PUT` 等は対象）
3. 対象リクエストからCSRFトークンを取得して検証
4. 検証失敗時は `400 Bad Request` を返す

CSRFトークンの送信先（クライアント → サーバー）：
- リクエストヘッダ: `X-CSRF-TOKEN`
- リクエストパラメータ: `csrf-token`

**基本設定**（Jakarta Server Pagesカスタムタグ使用時）

```xml
<!-- ハンドラ構成 -->
<component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
  <property name="handlerQueue">
    <list>
      <!-- セッションストアハンドラ -->
      <component-ref name="sessionStoreHandler" />

      <!-- Nablarchカスタムタグ制御ハンドラ -->
      <component-ref name="nablarchTagHandler"/>

      <!-- CSRFトークン検証ハンドラ（上記2つより後ろに配置） -->
      <component-ref name="csrfTokenVerificationHandler"/>
    </list>
  </property>
</component>

<component name="csrfTokenVerificationHandler"
           class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
```

Jakarta Server Pagesカスタムタグを使用している場合、CSRFトークンは画面に自動出力されるため、アプリケーションプログラマの実装は不要です。

**依存モジュール**

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

**ログイン時のトークン再生成**（セッションIDのみ再生成する実装の場合）

```java
CsrfTokenUtil.regenerateCsrfToken(request);
```

セッションストアを破棄して再生成する実装であれば不要です（CSRFトークンも一緒に破棄・再生成されるため）。

**注意点**:

- **セッションストアが必須**: CSRFトークンをセッションストアに格納するため、`セッション変数保存ハンドラ`より後ろに配置する必要があります
- **カスタムタグ使用時の配置順**: `Nablarchカスタムタグ制御ハンドラ`より後ろに配置すること
- **ファイルアップロード時**: ファイル保存前に検証したい場合は、`マルチパートリクエストハンドラ`の前に本ハンドラとセッションストアハンドラを配置する
- **リクエスト単体テスト**: 正しい画面遷移を経由しないためCSRF検証に失敗します。テスト時は `NopHandler` に差し替えて無効化してください：
  ```xml
  <component name="csrfTokenVerificationHandler" class="nablarch.test.NopHandler" />
  ```

参照: `handlers-csrf-token-verification-handler.json#s4`, `handlers-csrf-token-verification-handler.json#s3`, `handlers-csrf-token-verification-handler.json#s5`