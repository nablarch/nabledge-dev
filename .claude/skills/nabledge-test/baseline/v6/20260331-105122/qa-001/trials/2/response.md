**結論**: コード値のプルダウン入力には `n:codeSelect` カスタムタグを使用します。`codeId` 属性にコードIDを指定するだけで、コードマスタから選択肢を自動的に取得してプルダウンを生成できます。

**根拠**:

**1. 基本的な実装（n:codeSelect）**

JSPで以下のように記述します：

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" />
```

`codeId` に指定したコードIDのコードマスタから選択肢が自動取得されます。入力画面では `<select>` 要素として、確認画面では指定の `listFormat` 形式で出力されます。

**2. パターンで表示するコード値を絞り込む**

コードパターンテーブルに複数のパターンを定義している場合、`pattern` 属性で使用するパターンを指定できます：

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

**3. ラベル表示のカスタマイズ（labelPattern）**

`labelPattern` 属性でプルダウンのラベル表示をカスタマイズできます：

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

**4. 主要な属性一覧（n:codeSelect）**

| 属性名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | XHTMLのname属性 |
| codeId | ○ | | コードID |
| pattern | | 指定なし | 使用するパターンのカラム名 |
| withNoneOption | | `false` | 先頭に選択なしオプションを追加するか |

**5. バリデーション（入力値チェック）**

```java
@CodeValue(codeId = "GENDER")
private String gender;
```

**注意点**:
- `n:codeSelect` は入力画面では `<select>` 要素、確認画面では `listFormat` で指定した形式で出力されます

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-code.json#s2`
