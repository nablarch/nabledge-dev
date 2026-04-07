**結論**: コード値のプルダウン入力には `<n:codeSelect>` カスタムタグを使用します。`codeId` 属性にコードIDを指定するだけで、コード管理機能からコード値を取得してプルダウンを生成します。

**根拠**:

**基本的な使い方**

JSPに `<n:codeSelect>` タグを記述し、`name`（フォームのプロパティ名）と `codeId`（コードID）を指定します。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" />
```

- 入力画面では `<select>` タグを生成
- 確認画面では選択されたコード名称をテキスト表示（入力画面・確認画面のJSP共通化が可能）

**主要属性**

| 属性 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | フォームのプロパティ名 |
| `codeId` | ○ | コードID（コードマスタのID） |
| `pattern` | | 使用するパターンのカラム名（機能ごとの表示切り替え） |
| `optionColumnName` | | オプション名称のカラム名 |
| `labelPattern` | | ラベル整形パターン。`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$VALUE$`（コード値）、`$OPTIONALNAME$`（オプション名称） |

**パターンを使って表示するコード値を切り替える場合**

コードパターンテーブルのパターンカラムで機能ごとに表示・非表示を切り替えます。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

Java側でも同様のパターン指定が可能:
```java
List<String> pattern2 = CodeUtil.getValues("GENDER", "PATTERN2");
```

**ラベル書式をカスタマイズする場合**

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```
→ 入力画面: `<select name="form.gender"><option value="MALE">MALE-男</option>...`
→ 確認画面: `<div>FEMALE-女</div>`

**オプション名称を使う場合**

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" optionColumnName="KANA_NAME"
              cssClass="form-control" labelPattern="$OPTIONALNAME$"/>
```

**入力値バリデーション**

選択されたコード値が有効なコード範囲内かを検証するには `@CodeValue` アノテーションを使用します。

```java
// bean_validationの場合
@CodeValue(codeId = "GENDER")
private String gender;

// パターン指定でチェック範囲を絞る場合
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

**必要なMavenモジュール**

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

**注意点**:
- `<n:codeSelect>` はカスタムタグのため、JSP 2.1以降のWebコンテナが必要です
- カスタムタグでは言語指定によるコード値取得は不可。多言語対応が必要な場合は、アクション側で `CodeUtil`（ロケール指定API）を使用してリクエストスコープに設定し、`<n:select>` タグで表示する方法を検討してください
- パターン名はコードパターンテーブルのカラム名と**厳密に一致**させる必要があります（大文字小文字区別あり）

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-code.json#s2`, `component/libraries/libraries-code.json#s5`, `component/libraries/libraries-code.json#s6`