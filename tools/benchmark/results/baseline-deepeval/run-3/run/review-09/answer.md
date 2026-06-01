**結論**: `SecureHandler` に `ContentSecurityPolicyHeader` を追加することでCSPを有効にできる。JSPカスタムタグを使用している場合はnonce方式が必要で、`generateCspNonce` プロパティを `true` に設定する。

---

**根拠**:

#### 方法①: 固定のCSPヘッダを設定する（nonceなし）

スクリプトをすべて外部ファイルで管理しており、インラインスクリプトが一切ない場合に使用する。

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
      <component class="nablarch.fw.web.handler.secure.ReferrerPolicyHeader" />
      <component class="nablarch.fw.web.handler.secure.CacheControlHeader" />

      <!-- CSPヘッダを追加する -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self'" />
      </component>
    </list>
  </property>
</component>
```

出力例: `Content-Security-Policy: default-src 'self'`

---

#### 方法②: nonceを使ったCSP設定（JSPカスタムタグ使用時に推奨）

Nablarchの JSPカスタムタグは `formタグ` などで JavaScript を自動生成するため、nonce方式が必要。

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
        <!-- $cspNonceSource$ がリクエストごとに生成されたnonceに置換される -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

出力例: `Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`

`generateCspNonce=true` にすると、JSPカスタムタグが以下のように動作変更される:
- `formタグ` が生成するJavaScriptをscript要素にまとめ、nonce属性を自動設定
- `scriptタグ` が生成するscript要素にnonce属性を自動設定
- `<n:cspNonce />` タグでnonceを任意の要素に埋め込めるようになる

---

#### インライン要素にnonceを手動で埋め込む（`cspNonceタグ`）

既存のインラインスタイルなどにnonceを付与する場合:

```jsp
<style nonce="<n:cspNonce />">
  /* インラインスタイル */
</style>
```

---

#### report-onlyモード（本番導入前の動作確認に使用）

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <property name="reportOnly" value="true" />
</component>
```

出力: `Content-Security-Policy-Report-Only: ...`（ポリシー違反を報告するだけでブロックしない）

---

**注意点**:
- `SecureHandler` は `HTTPレスポンスハンドラ` よりも後ろに配置すること（ハンドラキューの順序）
- nonceはHTMLに埋め込まれるため、JSPから生成されるHTMLがリクエストごとに変化する（キャッシュに注意）
- JSPカスタムタグが生成する要素にJavaScriptを追加したい場合、`onclick` 属性でインラインスクリプトを指定するとCSPポリシーに違反する。代わりに `suppressDefaultSubmit="true"` を設定し、外部ファイルまたはnonce付きscript要素から `addEventListener` で処理を追加する

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag.json:s40

---