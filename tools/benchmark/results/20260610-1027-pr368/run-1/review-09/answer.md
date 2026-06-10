**結論**: NablarchのWeb画面でCSPを有効にするには、`SecureHandler`に`ContentSecurityPolicyHeader`を追加してポリシーを設定します。Nablarchカスタムタグ（JSP）を使用している場合は、nonceを生成する設定も合わせて行う必要があります。

**根拠**:

#### パターン1: 固定のCSPヘッダを設定する（nonceなし）

JavaScriptをインラインで使用しない場合はこちら。コンポーネント設定ファイルに`ContentSecurityPolicyHeader`を追加します。

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
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

これにより `Content-Security-Policy: default-src 'self'` がレスポンスヘッダに書き出されます。

#### パターン2: nonceを生成してCSPヘッダに設定する（Nablarchカスタムタグ使用時）

Nablarchカスタムタグ（JSP）を使用している場合、一部のカスタムタグがJavaScriptを出力するためnonceが必要です。

1. `SecureHandler`の`generateCspNonce`プロパティを`true`に設定する
2. `ContentSecurityPolicyHeader`のポリシーにプレースホルダー`$cspNonceSource$`を含める

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

`$cspNonceSource$`はリクエストごとに `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV` のような値に置換されます。

`generateCspNonce`を`true`にすると、カスタムタグの動作が以下のように自動的に変化します：
- `formタグ`が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ`が生成するscript要素にもnonce属性が自動設定される
- JSPで`<n:cspNonce />`タグによるnonce出力が可能になる

#### インラインstyleなどに手動でnonceを設定したい場合

```jsp
<%-- cspNonceタグを使用してnonce属性を設定する --%>
<style nonce="<n:cspNonce />">
  /* 省略 */
</style>
```

#### report-onlyモードで段階的に導入する場合

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only`ヘッダとして出力され、ポリシー違反をレポートするだけでブロックは行いません。

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも後ろに設定すること（ハンドラキューの順序）
- nonceを使う場合、JSPから生成されるHTMLはリクエストのたびに変化するため、キャッシュの扱いに注意が必要
- CSPのポリシー設計では、インラインスクリプト（onclick属性等）を避け、外部ファイルまたはnonce付きscript要素にまとめることが推奨される

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag.json:s40