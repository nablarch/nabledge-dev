**結論**: NablarchのCSP対応は、`SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシーを設定することで実現します。JSPカスタムタグを使用している場合はnonce方式が推奨されます。

**根拠**:

#### パターン1: 固定ポリシーの設定（nonce不使用）

コンポーネント設定ファイルに `ContentSecurityPolicyHeader` を追加します。

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

この設定で `Content-Security-Policy: default-src 'self'` ヘッダが出力されます。

#### パターン2: nonceを使用する設定（JSPカスタムタグを使用している場合に推奨）

NablarchのJSPカスタムタグは一部でJavaScriptを出力するため、nonce方式で対応します。

1. `SecureHandler` の `generateCspNonce` を `true` に設定
2. `policy` にプレースホルダー `$cspNonceSource$` を含める

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

`$cspNonceSource$` はリクエスト毎に生成されたnonceに置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` のように出力されます。

nonceを有効にすると、JSPカスタムタグの動作が以下のように自動で変化します：
- `formタグ` が生成するJavaScriptをscript要素にまとめ、nonce属性にnonceを自動設定
- `scriptタグ` が生成するscript要素のnonce属性にnonceを自動設定
- `cspNonceタグ` でJSP内にnonceを出力できるようになる

#### パターン3: report-onlyモード（段階的導入時）

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only` ヘッダが出力され、ポリシー違反をブロックせずに検知のみ行えます。

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに設定する必要があります
- `secureResponseHeaderList` に `ContentSecurityPolicyHeader` を追加する際は、デフォルトの他のヘッダコンポーネント（`FrameOptionsHeader` 等）も一緒に設定してください（省略すると他のセキュリティヘッダが出力されなくなります）
- nonceはHTMLに埋め込まれるため、JSPから生成されるHTMLがリクエスト毎に変化します

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38