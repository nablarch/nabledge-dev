**結論**: NablarchのWeb画面でCSPを設定するには、`SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシー文字列を設定します。インラインJavaScriptを含む場合はnonceを使った設定が必要です。

**根拠**:

### 方法1: 固定のCSPヘッダを設定する

`SecureHandler` の `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加し、`policy` にポリシーを設定します。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <!-- Content-Security-Policyを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- ポリシーを設定する -->
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

この設定により `Content-Security-Policy: default-src 'self'` レスポンスヘッダが出力されます。

### 方法2: nonceを使ったCSP設定（JSPカスタムタグを使っている場合）

NablarchのJSPカスタムタグはJavaScriptを出力するものがあるため、nonceを使った設定が必要です。

1. `SecureHandler` の `generateCspNonce` を `true` に設定
2. `ContentSecurityPolicyHeader` の `policy` にプレースホルダー `$cspNonceSource$` を含める

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <!-- nonceを生成するように設定する -->
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- nonceを含んだポリシーを設定する -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$` はリクエストごとに `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV` のような値に自動置換されます。

nonce生成を有効にすると、JSPカスタムタグの動作が以下のように変化します:
- `<n:script>` タグが生成する `<script>` 要素に自動でnonce属性が設定される
- `formタグ` が生成するJavaScriptが `<script>` 要素にまとめられnonce属性が付与される
- `<n:cspNonce />` タグでnonce値を任意の要素に埋め込めるようになる

### 方法3: report-onlyモード（本番適用前の検証）

ポリシーを強制せずに違反レポートのみ受け取りたい場合は `reportOnly` を `true` に設定します。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合 `Content-Security-Policy-Report-Only` ヘッダが出力されます。

### 既存のインラインスクリプト/スタイルへの対応

既存のインラインコードをすぐに外部ファイルへ移行できない場合は、`<n:cspNonce />` タグで対象要素にnonce属性を付与できます。

```jsp
<style nonce="<n:cspNonce />">
  /* インラインスタイル */
</style>
```

**注意点**:
- Nablarch の CSP 対応は **nonce を利用**する方式です。nonce はリクエストごとに生成されるため、JSP から生成される HTML はリクエストのたびに異なるコンテンツになります（キャッシュに注意）
- JSPカスタムタグを利用している場合は、固定ポリシーだけでは `unsafe-inline` を許可しない限りJavaScript実行がブロックされます。必ず方法2のnonce設定を使用してください
- スクリプトやスタイルは可能な限り**外部ファイル**として記述することが推奨されます
- `Content-Security-Policy` をレスポンスヘッダで設定できない場合は、`<n:cspNonce />` タグの `sourceFormat` 属性を `true` にして meta 要素で設定する代替手段もあります

参照: component/handlers/handlers-secure-handler.json#s6, component/handlers/handlers-secure-handler.json#s7, component/handlers/handlers-secure-handler.json#s8, component/handlers/handlers-secure-handler.json#s9, component/libraries/libraries-tag.json#s38, component/libraries/libraries-tag.json#s39