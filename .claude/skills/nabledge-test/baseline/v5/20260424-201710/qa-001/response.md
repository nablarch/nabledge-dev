**結論**: コード値のプルダウン入力を実装するには、Nablarch が提供する `<n:codeSelect>` カスタムタグを使用します。`codeId` 属性に表示したいコードID、`name` 属性に入力項目名を指定すれば、コード管理機能に登録されたコード名称テーブルの値がプルダウン（select/option）として出力されます。

**根拠**:

JSP での基本的な使用例 (libraries-tag.json#s30):

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

出力される HTML:

```html
<!-- 入力画面 -->
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>

<!-- 確認画面 -->
<div>FEMALE-女</div>
```

主な属性（libraries-tag-reference.json#s51）:

| 属性 | 必須 | 説明 |
|---|---|---|
| name | 必須 | XHTMLのname属性 |
| codeId | 必須 | コードID |
| pattern | 任意 | 使用するパターンのカラム名 |
| optionColumnName | 任意 | 取得するオプション名称のカラム名 |
| labelPattern | 任意 | ラベル整形パターン。`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値）が使用可能。デフォルトは `$NAME$` |
| withNoneOption | 任意 | リスト先頭に「選択なし」オプションを追加するか。デフォルト `false` |
| noneOptionLabel | 任意 | withNoneOption が `true` のときの先頭ラベル |
| multiple / size / disabled / tabindex / onchange など | 任意 | XHTML 標準属性 |
| nameAlias | 任意 | name属性のエイリアス（カンマ区切り） |

オプション名称を表示する例（libraries-code.json#s10）:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER"
              optionColumnName="KANA_NAME"
              cssClass="form-control"
              labelPattern="$OPTIONALNAME$"/>
```

パターンによる表示項目の絞り込み例（libraries-code.json#s7）:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

コード管理機能の前提として、コードパターンテーブル・コード名称テーブルを用意し、`CodePatternSchema.patternColumnNames` などを設定する必要があります（libraries-code.json#s7、#s8、#s9）。ソート順はコード名称テーブルの `SORT_ORDER` カラムで制御します。

**注意点**:

- カスタムタグ `<n:codeSelect>` は **言語指定によるコード値取得ができません**。内部で `CodeUtil` のロケール非指定 API を使用しているためです。言語を明示して値を取得したい場合は、アクション側で `CodeUtil.getName("GENDER", "MALE", Locale.JAPANESE)` などを呼び出してください（libraries-tag.json#s30、libraries-code.json#s8）。
- `$OPTIONALNAME$` を `labelPattern` に使う場合は `optionColumnName` 属性の指定が必須です。
- 開発基盤（テスティングフレームワーク）での画面試作では `/WEB-INF/tags/widget/field/code_pulldown.tag` ウィジェットが用意されており、ローカル動作時は `/js/devtool/resource/コード値定義.js` からコード名称を取得します（testing-framework-field-code-pulldown.json#s2, #s3）。

参照:
- component/libraries/libraries-tag.json#s30
- component/libraries/libraries-tag-reference.json#s51
- component/libraries/libraries-code.json#s7, #s8, #s9, #s10
- development-tools/testing-framework/testing-framework-field-code-pulldown.json#s2, #s3
