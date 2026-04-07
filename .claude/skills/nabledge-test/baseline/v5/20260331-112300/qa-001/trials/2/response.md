**結論**: コード値のプルダウン入力を実装するには、`n:codeSelect` カスタムタグを使用し、`codeId` 属性にコードIDを指定します。UI開発基盤を使用する場合は `field:code_pulldown` ウィジェットを使用します。

**根拠**:

**必要なモジュール:**
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

**JSP実装例（`n:codeSelect` カスタムタグ）:**
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```

- 入力画面では `<select>` タグが出力される
- 確認画面では選択されたコード値のラベルがテキストで出力される

**主要属性:**
| 属性 | 内容 | 必須/任意 |
|---|---|---|
| `codeId` | コード定義ID | 必須 |
| `pattern` | 使用するコードパターンのカラム名（デフォルト: 指定なし） | 任意 |
| `optionColumnName` | オプション名称のカラム名 | 任意 |
| `labelPattern` | ラベル表示書式（`$NAME$`、`$SHORTNAME$`、`$OPTIONALNAME$`、`$VALUE$`） | 任意（デフォルト: `$NAME$`） |
| `withNoneOption` | リスト先頭に選択なしオプションを追加するか（デフォルト: false） | 任意 |

**コードパターンで機能ごとに表示を切り替える場合:**
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

パターン名は設定ファイルで設定したカラム名と**厳密に一致**させる必要がある。

**UI開発基盤（テスティングフレームワーク）を使用する場合:**

ウィジェット `field:code_pulldown` を使用する:
```jsp
<%-- 設計成果物（ローカル動作） --%>
<field:code_pulldown
  title="性別"
  codeId="GENDER"
  pattern="PATTERN01"
  sample="[男性]|女性">
</field:code_pulldown>
```

**注意点**:
- カスタムタグでは言語指定によるコード値取得は不可。言語指定が必要な場合は、アクションで `CodeUtil` を使用すること
- `pattern` 属性のパターン名は、設定ファイルで設定したカラム名と**厳密に一致**させる必要がある
- `labelPattern` に `$OPTIONALNAME$` を使用する場合は `optionColumnName` の指定が必須

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-code.json#s2`, `development-tools/testing-framework/testing-framework-field_code_pulldown.json#s2`