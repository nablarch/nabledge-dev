**結論**: NablarchのウェブアプリケーションでCSPを有効にするには、`SecureHandler`に`ContentSecurityPolicyHeader`を設定してレスポンスヘッダを出力し、nonceを使う場合は`generateCspNonce`プロパティを`true`にした上でJSPに`<n:cspNonce />`タグを組み合わせる。

**根拠**:

#### 方法1: 固定のContent-Security-Policyヘッダを設定する

コンポーネント設定ファイルの`SecureHandler`に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシー文字列を設定する。

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

この設定で `Content-Security-Policy: default-src 'self'` のようなレスポンスヘッダが出力される。

#### 方法2: nonceを生成してCSPに対応する（JSPカスタムタグと組み合わせる場合）

NablarchのJSPカスタムタグはJavaScriptを生成するため、nonceを使って対応する。

**ハンドラの設定:**

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

      <!-- Content-Security-Policyを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- nonceを含んだポリシーを設定する -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

プレースホルダー `$cspNonceSource$` はリクエスト毎に生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` のようなヘッダが出力される。

この設定を行うと、`<n:formタグ>`や`<n:scriptタグ>`が生成するscript要素に自動でnonce属性が設定される。

任意の要素（例: style要素）にnonceを設定したい場合は`<n:cspNonce />`タグを使用する:

```jsp
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

#### 方法3: report-onlyモード（動作確認用）

本番適用前の確認として、ポリシー違反を報告するだけで制限しないモードも利用できる:

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only` ヘッダが出力される。

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも後ろ（内側）に設定すること（`HTTPレスポンスハンドラ`がServletのレスポンスオブジェクトにヘッダを設定するため）。
- nonceを使う場合、生成されるHTMLはリクエスト毎に変化する。
- `secureResponseHeaderList`を設定する際は、デフォルトで適用されていた他のヘッダコンポーネント（`FrameOptionsHeader`等）も一緒に列挙すること。

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39