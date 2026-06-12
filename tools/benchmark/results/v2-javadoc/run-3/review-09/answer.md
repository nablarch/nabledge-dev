十分な情報が揃いました。Step 5の回答生成に進みます。

**Step 6: 検証**

回答に含めるNablarch固有の主張を検証します：
- `SecureHandler`の`generateCspNonce`プロパティ → s8に明記 ✅
- `ContentSecurityPolicyHeader`クラス → s7/s8に明記 ✅
- `$cspNonceSource$`プレースホルダー → s8に明記 ✅
- `reportOnly`プロパティ → s9に明記 ✅
- `cspNonceタグ` → s56に明記 ✅
- formタグとscriptタグへの自動nonce付与 → s38に明記 ✅

verify_result = PASS

---

**結論**: NablarchのWeb画面でCSPを設定するには、`SecureHandler`に`ContentSecurityPolicyHeader`を追加します。nonceを使う場合は`generateCspNonce`プロパティを`true`にし、JSPのカスタムタグと連携させます。

**根拠**:

**パターン1: 固定のCSPポリシーを設定する**（nonceが不要な場合）

コンポーネント設定ファイルに`ContentSecurityPolicyHeader`を追加し、`policy`にポリシー文字列を指定します。

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

これにより `Content-Security-Policy: default-src 'self'` ヘッダが出力されます。

---

**パターン2: nonceを使ってCSPを設定する**（Nablarchカスタムタグを使用している場合の推奨）

Nablarchのカスタムタグ（formタグ、scriptタグなど）は一部のJavaScriptを生成するため、nonceによる対応が必要です。

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
        <!-- プレースホルダー $cspNonceSource$ にnonceが埋め込まれる -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

`$cspNonceSource$`はリクエストごとに生成されたnonceで置換され、例えば `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'` として出力されます。

`generateCspNonce`を`true`にすると、カスタムタグの動作が自動的に変化します：
- `formタグ`が生成するJavaScriptをscript要素にまとめ、nonce属性を自動設定
- `scriptタグ`が生成するscript要素にnonce属性を自動設定

任意の要素（例：style要素）にnonceを設定したい場合は`cspNonceタグ`を使います：

```jsp
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

---

**パターン3: report-onlyモードで動作させる**（導入前の検証用）

`reportOnly`を`true`に設定します。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

これにより`Content-Security-Policy-Report-Only`ヘッダが出力されます。

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも後ろに設定すること（ハンドラキューの順序に注意）
- `secureResponseHeaderList`を明示的に設定する場合は、デフォルトヘッダ（`FrameOptionsHeader`等）も必ずリストに含めること（省略するとデフォルトヘッダが出力されなくなる）
- nonceはHTML内に埋め込まれるため、JSPから生成されるHTMLはリクエストの都度変化する

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag-reference.json:s56

---