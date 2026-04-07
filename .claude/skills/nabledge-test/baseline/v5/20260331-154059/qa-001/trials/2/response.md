**結論**: コード値のプルダウン入力を実装するには、`n:codeSelect` カスタムタグを使用します。`codeId` 属性にコードIDを指定するだけで、コード管理機能からコード値の一覧を取得してプルダウンを生成できます。

**根拠**:

**基本的な使い方**:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" />
```

- 入力画面では `<select>` タグが出力される
- 確認画面では選択されたコード名称が出力される（入力画面と確認画面でJSPを共通化可能）

**パターンを指定して表示するコード値を絞り込む**:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

コードパターンテーブルのパターン列で機能ごとに表示・非表示を切り替える。`pattern` 属性に指定するパターン名は設定ファイルのカラム名と**厳密に一致**させる必要がある。

**ラベル表示書式をカスタマイズする**:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```

`labelPattern` 属性で使用できるプレースホルダ:
- `$NAME$`: コード名称（デフォルト）
- `$SHORTNAME$`: 略称
- `$OPTIONALNAME$`: オプション名称（`optionColumnName` 属性の指定も必須）
- `$VALUE$`: コード値

**オプション名称を使用する**:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER"
              optionColumnName="KANA_NAME" labelPattern="$OPTIONALNAME$" />
```

**入力値のバリデーション**:

選択したコード値が有効なコード値かをバリデーションする場合は `@CodeValue` アノテーションを使用する。

bean_validationの場合:
```java
@CodeValue(codeId = "GENDER")
private String gender;
```

nablarch_validationの場合:
```java
@CodeValue(codeId = "GENDER")
public void setGender(String gender) { this.gender = gender; }
```

パターンを指定して有効値を絞り込む場合:
```java
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

**必要なMavenモジュール**:

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
- カスタムタグでは言語指定によるコード値取得は不可。`CodeUtil` のロケール未指定APIを使用しているため。言語指定が必要な場合は、アクションで `CodeUtil` を使用すること。
- `pattern` 属性のパターン名は、設定ファイルに設定したカラム名と厳密に一致させる必要がある。
- `$OPTIONALNAME$` を `labelPattern` で使用する場合は `optionColumnName` 属性の指定が必須。

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-code.json#s2`, `component/libraries/libraries-code.json#s5`, `component/libraries/libraries-code.json#s6`