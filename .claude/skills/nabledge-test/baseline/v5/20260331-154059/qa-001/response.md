**結論**: コード値のプルダウン入力を実装するには、`n:codeSelect` カスタムタグを使用し、`codeId` 属性にコードIDを指定します。

**根拠**:

コード管理機能と連携したプルダウンは `n:codeSelect` カスタムタグで実装します。

**基本的な使い方**:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" cssClass="form-control" />
```

- `name`: フォームのプロパティ名
- `codeId`: コードマスタのコードID

**コードパターンで表示・非表示を切り替える場合**:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

- `pattern` 属性にコードパターンテーブルのカラム名を指定します（例: `PATTERN1`, `PATTERN2`）
- パターン名は設定ファイルで設定した `CodePatternSchema.patternColumnNames` のカラム名と**厳密に一致**させる必要があります

**ラベル表示をカスタマイズする場合**:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```

`labelPattern` のプレースホルダ:
- `$NAME$`: コード名称（デフォルト）
- `$SHORTNAME$`: 略称
- `$VALUE$`: コード値
- `$OPTIONALNAME$`: オプション名称（`optionColumnName` 指定必須）

**確認画面での表示**:

`n:codeSelect` は入力画面では `<select>` タグ、確認画面ではラベル文字列として自動切り替えされます。

```
<!-- 入力画面 -->
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>

<!-- 確認画面 -->
<div>FEMALE-女</div>
```

**注意点**:
- カスタムタグでは言語指定によるコード値取得は不可。言語指定が必要な場合は、アクションで `CodeUtil` を直接使用すること
- `pattern` 属性のカラム名は `CodePatternSchema.patternColumnNames` の設定と厳密に一致させること
- 必要なモジュール: `nablarch-common-code` および `nablarch-common-code-jdbc`

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-code.json#s2`