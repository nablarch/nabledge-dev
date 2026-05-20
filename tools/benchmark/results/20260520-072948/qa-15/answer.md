**結論**: NablarchのカスタムタグはデフォルトでHTMLエスケープを行うため、カスタムタグ経由の出力ではXSSの根本的解決（IPA 5-(i)）が可能です。ただし、JavaScript部分のエスケープやURL出力の制限はNablarch未対応であり、プロジェクト側での対応が必要です。

**根拠**:

**カスタムタグが対応する範囲（〇）**

カスタムタグは原則として出力時に全てのHTML属性をHTMLエスケープします。変換内容：

| 文字 | 変換後 |
|------|--------|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&#034;` |
| `'` | `&#039;` |

EL式はHTMLエスケープを行わないため、値の出力には必ず `writeタグ` などのカスタムタグを使用してください。

**Nablarch未対応の項目（×、プロジェクト対応が必要）**

| IPA対策 | 内容 | Nablarch対応 |
|---------|------|-------------|
| 5-(i) | HTMLエスケープ | 〇 カスタムタグで対応 |
| 5-(ii) | URL出力を http/https のみ許可 | × |
| 5-(iii) | `<script>` 要素の動的生成禁止 | × |
| 5-(iv) | 外部スタイルシート取り込み禁止 | × |

**セキュアハンドラによる保険的対策（〇）**

セキュアハンドラを使うことで、ブラウザのXSS対策機能を有効化するレスポンスヘッダを返せます：

```xml
<component class="nablarch.fw.web.handler.SecureHandler">
  <property name="secureResponseHeaderList">
    <list>
      <component class="nablarch.fw.web.handler.secure.XssProtectionHeader" />
      <component class="nablarch.fw.web.handler.secure.FrameOptionsHeader">
        <property name="option" value="DENY" />
      </component>
      <component class="nablarch.fw.web.handler.secure.ContentTypeOptionsHeader" />
    </list>
  </property>
</component>
```

また、HTTP文字エンコード制御ハンドラにより Content-Type の charset が設定され、特定ブラウザでのエスケープ迂回XSSも防止できます。

**注意点**:
- `rawWriteタグ` はHTMLエスケープなしで出力します。不特定ユーザが設定できる値に使用した場合、XSS脆弱性の直接の原因となります。
- `prettyPrintタグ` は非推奨です（設定不備によるXSSリスクあり）。利用者が任意の装飾を施す機能が必要な場合は、OSSのHTMLパーサでバリデーション → `rawWriteタグ` で出力、またはMarkdown入力＋クライアントサイド変換の方式を検討してください。
- JavaScriptのエスケープ処理はカスタムタグでは提供されていません。scriptタグのボディや `onclick` 属性などに動的な値を埋め込む場合は、プロジェクトの責任でエスケープ処理を実施してください。

参照: `security-check-2.チェックリスト.json:s21`, `security-check-2.チェックリスト.json:s22`, `security-check-2.チェックリスト.json:s23`, `security-check-2.チェックリスト.json:s24`, `security-check-2.チェックリスト.json:s28`, `security-check-2.チェックリスト.json:s30`, `libraries-tag.json:s2`, `libraries-tag.json:s27`, `libraries-tag.json:s50`, `handlers-secure-handler.json:s4`