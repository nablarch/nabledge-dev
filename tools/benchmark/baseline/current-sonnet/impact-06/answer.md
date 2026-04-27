**結論**: Nablarchのカスタムタグ（`<n:submit>` 等）が出力する `onclick` インラインJavaScriptについては、**JSPの書き方を変えずに**対応できる。`SecureHandler` の nonce 生成機能を有効にすると、カスタムタグが onclick のコードを自動的に `<script nonce="...">` 要素に移動する。ただし、アプリケーション独自に書いた `onclick="自前の処理"` は自動対応されないため、個別対処が必要。

**根拠**:

① **カスタムタグが出力する onclick の自動対応**  
`SecureHandler` の `generateCspNonce` を `true` にすると、`<n:form>` が生成するJavaScript（onclick属性のサブミット関数呼び出しを含む）は **script 要素にまとめられ、nonce 属性が自動付与される** ように動作が変わる。JSP側の記述変更は不要。（`component/libraries/libraries-tag.json:s9`）

② **設定手順（SecureHandler + ContentSecurityPolicyHeader）**  
```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="generateCspNonce" value="true" />
  <property name="secureResponseHeaderList">
    <list>
      ...
      <component class="nablarch.fw.web.handler.secure.ContentSecurityPolicyHeader">
        <property name="policy" value="default-src 'self' '$cspNonceSource$'" />
      </component>
    </list>
  </property>
</component>
```
`$cspNonceSource$` はリクエスト毎に生成された nonce（例: `nonce-DhcnhD3khTMePgXwdayK9BsMqXjhguVV`）に自動置換される。（`component/handlers/handlers-secure_handler.json:s8`）

③ **独自インラインJavaScriptへの対処**  
nonce 自動付与はカスタムタグが生成するコードのみが対象。JSPに直接書いた `onclick="独自処理"` や `onchange="..."` には適用されない。これらは以下のいずれかで対応する：
- `<n:cspNonce />` タグで nonce 値を取得して `<script nonce="<n:cspNonce />">` ブロックに移行する
- 外部 JS ファイルに処理を移して `<n:script>` タグで読み込む（nonce 自動付与対象になる）
（`component/libraries/libraries-tag.json:s10`、`component/libraries/libraries-tag.json:s3`、`component/libraries/libraries-tag.json:s4`）

**注意点**:

- nonce はリクエスト毎に変わるため、CSP nonce を使う場合は HTML がキャッシュされないようにすること。（`component/libraries/libraries-tag.json:s9`）
- `unsafe-inline` や `unsafe-hashes` を CSP ポリシーに追加するのは避けること。インラインスクリプトへの攻撃を許可することになり CSP の効果が失われる。（`component/libraries/libraries-tag.json:s3`）
- `onchange` 等でサブミットボタンの `.click()` を呼び出す実装も同様に外部スクリプトへの移行を推奨。（`component/libraries/libraries-tag.json:s4`）
- CSP 対応の全体的な設定フローは `SecureHandler` の CSP 節を参照。（`component/handlers/handlers-secure_handler.json:s6`）

参照: component/libraries/libraries-tag.json:s9, component/handlers/handlers-secure_handler.json:s8, component/handlers/handlers-secure_handler.json:s6, component/libraries/libraries-tag.json:s10, component/libraries/libraries-tag.json:s3, component/libraries/libraries-tag.json:s4