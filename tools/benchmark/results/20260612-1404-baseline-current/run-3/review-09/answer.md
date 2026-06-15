**結論**: NablarchのWeb画面でCSPを有効にするには、`SecureHandler`に`ContentSecurityPolicyHeader`を追加してポリシーを設定する。nonceベースのCSP（インラインスクリプト対応）が必要な場合は、`generateCspNonce`プロパティを`true`にし、JSPカスタムタグと連携させる。

**根拠**:

**① 固定のContent-Security-Policyヘッダを設定する場合**

コンポーネント設定ファイルで`SecureHandler`の`secureResponseHeaderList`に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシー文字列を設定する。

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

この設定で `Content-Security-Policy: default-src 'self'` ヘッダが出力される。

**② nonceを使ってインラインスクリプトに対応する場合**

NablarchのJSPカスタムタグはJavaScriptを出力するものがあるため、nonceを使う方式が推奨される。

1. `SecureHandler`の`generateCspNonce`プロパティを`true`に設定する
2. `policy`にプレースホルダー`$cspNonceSource$`を含める（実行時に `nonce-[生成値]` に置換される）

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

nonceを有効にすると、JSPカスタムタグの動作が以下のように変化する：

- `formタグ`が生成するJavaScriptをscript要素にまとめ、nonce属性にnonceを自動設定する
- `scriptタグ`が生成するscript要素のnonce属性にnonceを自動設定する
- `cspNonceタグ`でJSP内にnonceを出力できるようになる（`sourceFormat="true"`でmeta要素用の`nonce-`プレフィックス付きで出力可能）

**③ report-onlyモード（段階的導入時）**

`ContentSecurityPolicyHeader`の`reportOnly`プロパティを`true`にすると、`Content-Security-Policy-Report-Only`ヘッダが出力される（ブロックせずに違反をレポートのみ）。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

**注意点**:
- `SecureHandler`は[HTTPレスポンスハンドラ]よりも**後ろ**に設定すること（`SecureHandler`で設定したヘッダをHTTPレスポンスハンドラがServlet APIのレスポンスオブジェクトに設定するため）
- nonceを使う場合、HTMLがリクエストの都度変化するため、レスポンスキャッシュの仕組みと注意して組み合わせること

参照: component/handlers/handlers-secure-handler.json:s6, component/handlers/handlers-secure-handler.json:s7, component/handlers/handlers-secure-handler.json:s8, component/handlers/handlers-secure-handler.json:s9, component/libraries/libraries-tag.json:s38, component/libraries/libraries-tag-reference.json:s56