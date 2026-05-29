Step 5-7: 回答を生成し、検証します。

**結論**: NablarchのウェブアプリケーションでCSPを設定するには、`SecureHandler`のコンポーネント定義に`ContentSecurityPolicyHeader`を追加する。nonceを使う場合は`generateCspNonce="true"`も合わせて設定し、JSPカスタムタグのnonce自動付与機能を活用する。

---

**根拠**:

### パターン1: 固定ポリシー

`SecureHandler`の`secureResponseHeaderList`に`ContentSecurityPolicyHeader`を追加し、`policy`プロパティにポリシー文字列を設定する。

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

### パターン2: nonceを使ったポリシー（推奨）

JSPカスタムタグを使用している場合はnonce方式を使う。`generateCspNonce="true"`を設定し、ポリシーにプレースホルダー`$cspNonceSource$`を含める。

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

`$cspNonceSource$`は`nonce-[生成されたnonce]`に置換され、例えば`Content-Security-Policy: default-src 'self' 'nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV'`のようなヘッダが出力される。

**nonceを有効にした場合のJSPカスタムタグの動作変化:**
- `formタグ`が生成するJavaScriptはscript要素にまとめられ、nonce属性にnonceが自動設定される
- `scriptタグ`が生成するscript要素のnonce属性にnonceが自動設定される
- `<n:cspNonce />`タグで任意の要素（style要素など）にnonceを埋め込めるようになる

**任意の要素へのnonce埋め込み例（style要素）:**

```jsp
<style nonce="<n:cspNonce />">
  <!-- 省略 -->
</style>
```

出力されるHTML:

```html
<style nonce="DhcnhD3khTMePgXwdayK9BsMqXjhguVV">
  <!-- 省略 -->
</style>
```

### report-onlyモード

本番適用前の確認には`reportOnly="true"`を設定する。`Content-Security-Policy-Report-Only`ヘッダが出力される。

```xml
<component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
  <property name="policy" value="default-src 'self'; report-uri http://example.com/report" />
  <!-- report-onlyモードで動作させる -->
  <property name="reportOnly" value="true" />
</component>
```

### CSPを守りながらJavaScript処理を追加する場合

カスタムタグが生成する要素に対してJavaScriptで処理を追加したい場合、onclick属性などのインラインスクリプトを使うとポリシーを緩める必要が生じる。代わりに以下の手順を使う。

1. id属性やname属性で要素を特定できるように設定する
2. 追加処理は外部ファイルまたはnonce付きscript要素として作成する
3. カスタムタグのデフォルトJavaScript生成は`suppressDefaultSubmit="true"`で抑制する

```jsp
<n:submit id="register_button" type="submit" uri="register"
          suppressDefaultSubmit="true" value="登録" />
```

```javascript
document.querySelector('#register_button').addEventListener('click', popUpConfirmation);
```

---

**注意点**:
- `SecureHandler`は`HTTPレスポンスハンドラ`よりも**後ろ**に設定すること（HTTPレスポンスハンドラがServlet APIのレスポンスオブジェクトにヘッダを設定するため）
- nonceを有効にすると、nonceがHTMLに埋め込まれるため、JSPから生成されるHTMLがリクエストの都度変化する

参照: `handlers-secure-handler.json:s6`, `handlers-secure-handler.json:s7`, `handlers-secure-handler.json:s8`, `handlers-secure-handler.json:s9`, `libraries-tag.json:s38`, `libraries-tag.json:s39`, `libraries-tag.json:s40`, `libraries-tag-reference.json:s56`, `handlers-secure-handler.json:s3`

---