**結論**: NablarchウェブアプリケーションでCSPを設定するには、`SecureHandler`に`ContentSecurityPolicyHeader`を追加します。固定ポリシーの設定とnonceを使う設定の2方式があります。

**根拠**:

### 方法1: 固定のContent-Security-Policyヘッダを設定する

`ContentSecurityPolicyHeader`を`SecureHandler`の`secureResponseHeaderList`に追加し、`policy`プロパティにCSPポリシーを指定します。

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

この設定により `Content-Security-Policy: default-src 'self'` がレスポンスヘッダに出力されます。

### 方法2: nonceを使って設定する（カスタムタグ使用時の推奨）

NablarchのJSPカスタムタグはJavaScriptを出力するため、nonceを使う方式が推奨されます。

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
        <!-- $cspNonceSource$ プレースホルダーを含める -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$`は`nonce-[生成されたnonce]`に置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` のように出力されます。

`generateCspNonce`を有効にすると、カスタムタグの動作が次のように自動変化します：
- `formタグ`が生成するJavaScriptがscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ`が生成するscript要素のnonce属性にnonceが自動設定される
- `cspNonceタグ`（`<n:cspNonce />`）でnonce値を任意の要素に埋め込める

### 方法3: report-onlyモードで動作させる（段階導入時）

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only`ヘッダが出力され、ポリシー違反を実際にブロックせずに検知できます。

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも後ろに設定すること（制約）
- `secureResponseHeaderList`を明示的に設定する場合、デフォルトのコンポーネント（`FrameOptionsHeader`等）もリストに含める必要がある
- カスタムタグを使用している場合は、nonce方式を使う方がCSP対応として適切

参照: `handlers-secure-handler.json:s6` `handlers-secure-handler.json:s7` `handlers-secure-handler.json:s8` `handlers-secure-handler.json:s9` `libraries-tag.json:s38` `libraries-tag.json:s39`