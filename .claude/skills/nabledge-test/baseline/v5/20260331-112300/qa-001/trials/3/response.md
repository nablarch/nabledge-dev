**結論**: コード値のプルダウン入力を実装するには、JSPで `<n:codeSelect>` カスタムタグを使用し、`codeId` 属性にコードIDを指定します。

**根拠**:

**必要なモジュール**（`pom.xml`に追加）:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-code</artifactId>
</dependency>
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-code-jdbc</artifactId>
</dependency>
```

**基本的な実装例（JSP）**:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

**主要属性**:

| 属性名 | 説明 |
|---|---|
| `codeId` | コードID（必須） |
| `pattern` | 使用するコードパターンのカラム名（デフォルト: 指定なし） |
| `optionColumnName` | オプション名称のカラム名 |
| `labelPattern` | ラベル表示書式。プレースホルダ: `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値）。デフォルト: `$NAME$` |

**実装例（パターンとラベル書式を指定）**:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```
入力画面では `<select>` タグとして出力され、確認画面では `<div>` タグとして出力されます（入力・確認画面のJSPを共通化可能）。

**オプション名称を使用する場合**:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" optionColumnName="KANA_NAME" cssClass="form-control" labelPattern="$OPTIONALNAME$"/>
```

**UIウィジェット（UI開発基盤）を使用する場合**:

`field:code_pulldown` ウィジェットを使用します。

設計成果物（ローカル動作）:
```jsp
<field:code_pulldown
  title="ユーザIDロック">
</field:code_pulldown>
```

実装成果物（サーバ動作）:
```jsp
<field:code_pulldown
  title            = "ユーザIDロック"
  name             = "11AC_W11AC01.userIdLocked"
  codeId           = "C0000001"
  pattern          = "PATTERN01"
  optionColumnName = "OPTION01"
  labelPattern     = "$OPTIONALNAME$">
</field:code_pulldown>
```

**注意点**:
- パターン名は設定ファイルで設定したカラム名と**厳密に一致**させる必要があります。
- カスタムタグでは言語指定によるコード値取得は不可です。言語指定が必要な場合は、アクションで `CodeUtil` を使用してください。
- `optionColumnName` を使用する場合は、`labelPattern` に `$OPTIONALNAME$` を指定してください。

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-code.json#s2`, `component/libraries/libraries-code.json#s5`, `development-tools/testing-framework/testing-framework-field_code_pulldown.json#s1`