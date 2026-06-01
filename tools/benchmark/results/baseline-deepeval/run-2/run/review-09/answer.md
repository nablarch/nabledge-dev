**結論**: `SecureHandler` に `ContentSecurityPolicyHeader` を追加することで `Content-Security-Policy` ヘッダが有効になる。Nablarchのカスタムタグ（JSP）でJavaScriptを出力している場合は、nonceを使ったCSP対応が必要。

---

**根拠**:

**パターン1: 固定ポリシーを設定する（最小構成）**

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

これにより `Content-Security-Policy: default-src 'self'` ヘッダが出力される。

---

**パターン2: nonceを使ったCSP（Nablarchカスタムタグ使用時は必須）**

Nablarchのカスタムタグ（formタグ、scriptタグ等）は一部のJavaScriptをインラインで生成するため、nonceを使ったCSP対応が必要。

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

`$cspNonceSource$` はリクエストごとに `nonce-[生成されたnonce値]` に置換される（例: `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`）。

このとき、カスタムタグの動作が自動的に変化する:
- `formタグ` が生成するJavaScriptはscript要素にまとめられ、nonce属性が自動設定される
- `scriptタグ` が生成するscript要素にもnonce属性が自動設定される

任意の場所でnonceを出力したい場合は `cspNonceタグ` を使用する（`sourceFormat="true"` でプレフィックス `nonce-` を付与できる）。

---

**パターン3: report-onlyモード（段階的導入に有効）**

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

`Content-Security-Policy-Report-Only` ヘッダが出力され、違反を検知するが実際のブロックは行わない。

---

**注意点**:
- `secureResponseHeaderList` を明示設定する場合は、デフォルトで付与されていた他のヘッダ（`FrameOptionsHeader` 等）も明示的に設定する必要がある（設定しないと除外される）
- nonceを使用するとHTMLはリクエストごとに動的に変化するため、CDNキャッシュ等に注意が必要

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag-reference.json:s56

---