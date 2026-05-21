**結論**: NablarchウェブアプリケーションでCSPを有効にするには、`SecureHandler` に `ContentSecurityPolicyHeader` を追加してポリシーを設定する。JSPカスタムタグを使用している場合は `generateCspNonce` を有効にしてnonceベースのCSPに対応する。

**根拠**:

**方法1: 固定のContent-Security-Policyヘッダを設定する**

コンポーネント設定ファイルの `SecureHandler` に `ContentSecurityPolicyHeader` を追加し、`policy` プロパティにCSPポリシー文字列を設定する。

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

この設定により、`Content-Security-Policy: default-src 'self'` のレスポンスヘッダが付与される。

**方法2: nonceを生成してContent-Security-Policyヘッダに設定する（JSPカスタムタグを使用している場合の推奨方法）**

JSPカスタムタグを使用している場合、一部のタグはJavaScriptを出力するため、nonceを使った対応が必要になる。手順は以下の通り。

1. `SecureHandler` の `generateCspNonce` プロパティを `true` に設定する
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

      <!-- Content-Security-Policyを付与するコンポーネント -->
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <!-- nonceを含んだポリシーを設定する -->
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```

プレースホルダー `$cspNonceSource$` はリクエストごとに生成されたnonce値（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）に置換される。nonceが有効になると、JSPカスタムタグの動作が以下のように変化する。

- `formタグ` が生成するJavaScriptをscript要素にまとめ、nonce属性に生成したnonceを自動設定する（onclick属性に指定する関数呼び出しも含む）
- `scriptタグ` が生成するscript要素のnonce属性に生成したnonceを自動設定する
- `cspNonceタグ`（`<n:cspNonce />`）で任意の要素にnonceを設定できるようになる

任意の要素にnonceを設定したい場合（style要素など）は `cspNonceタグ` を使用する。

```jsp
<%-- cspNonceタグを使用してnonce属性を設定する --%>
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

**方法3: report-onlyモードで動作させる（段階的な導入に有効）**

まず違反を検知だけしてブロックしない `report-only` モードで動かしたい場合は、`ContentSecurityPolicyHeader` の `reportOnly` を `true` に設定する。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

この場合、`Content-Security-Policy-Report-Only` ヘッダが付与される。

**注意点**:
- nonceを使用する場合、JSPから生成されるHTMLがリクエストのたびに変化する。
- カスタムタグが生成する要素にJavaScriptで処理を追加する場合、onclick属性にインラインスクリプトを指定すると `unsafe-inline` が必要になりCSPのセキュリティレベルが低下する。外部ファイルまたはnonce付きのscript要素に処理を実装し、`suppressDefaultSubmit="true"` を設定してカスタムタグによるデフォルトのJavaScript生成を抑制した上で、セレクタで要素を特定してイベントリスナーを登録する方法を推奨する。

参照: handlers-secure-handler.json:s6, handlers-secure-handler.json:s7, handlers-secure-handler.json:s8, handlers-secure-handler.json:s9, libraries-tag.json:s38, libraries-tag.json:s39, libraries-tag.json:s40

---