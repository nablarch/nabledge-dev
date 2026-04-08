**結論**: コード値のプルダウン入力は `n:codeSelect` カスタムタグを使用して実装します。アクション側でコードID を指定し、JSP側でタグの属性にコードID・パターン・ラベルパターンを設定することで実現できます。

**根拠**:

JSP でのコード値プルダウン実装例:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```

出力例（`form.gender="FEMALE"`の場合）:
```html
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>
```

**n:codeSelect タグの主要属性**:
- `name`: フォームのプロパティ名
- `codeId`: コード定義ID（必須）
- `pattern`: 使用するコードパターンのカラム名（デフォルト: 指定なし）
- `optionColumnName`: 取得するオプション名称のカラム名
- `labelPattern`: ラベル整形パターン。プレースホルダ: `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値）。デフォルト: `$NAME$`

アクション側での実装は不要です。JSP のカスタムタグのみで実現でき、フレームワークが コードID から自動的にコード値を取得します。
