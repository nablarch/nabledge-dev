**結論**: コード値のプルダウン入力には `n:codeSelect` カスタムタグを使用します。コードIDを指定するだけで、コードマスタから自動的に選択肢を取得してプルダウンを表示できます。

**根拠**:

#### 1. `n:codeSelect` タグの基本的な使い方

JSPで `n:codeSelect` タグを使用します。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" cssClass="form-control" />
```

| 属性 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | フォームのプロパティ名 |
| `codeId` | ○ | コードID（コードマスタに登録されたID） |
| `pattern` | | 使用するパターンのカラム名（省略時は全コード値） |
| `labelPattern` | | ラベル整形パターン（`$NAME$`=コード名称、`$VALUE$`=コード値など） |
| `withNoneOption` | | 先頭に選択なしオプションを追加するか（`true`/`false`） |
| `optionColumnName` | | 取得するオプション名称のカラム名 |

- 入力画面: `<select>` 要素で出力
- 確認画面: `listFormat` 属性で指定した形式で出力（デフォルト: `br`）

#### 2. パターンを使用して表示するコード値を絞り込む

コードパターンテーブルにパターン列を定義することで、機能ごとに表示するコード値を切り替えられます。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

```java
// Javaでパターン指定取得
List<String> pattern2 = CodeUtil.getValues("GENDER", "PATTERN2");
```

#### 3. ラベル整形パターン

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
<!-- 入力画面: <select>要素で出力、確認画面: <div>要素で出力 -->
```

#### 4. オプション名称を表示する

コード名称テーブルにオプション名称カラムを追加している場合:

```jsp
<n:codeSelect name="form.gender" codeId="GENDER"
              optionColumnName="KANA_NAME"
              labelPattern="$OPTIONALNAME$"
              cssClass="form-control" />
```

#### 5. バリデーション

入力値が有効なコード値かチェックするには `@CodeValue` アノテーションを使用します。

Bean Validation の場合:
```java
@CodeValue(codeId = "GENDER")
private String gender;
```

パターンを使用して選択値を制限した場合:
```java
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

#### 6. モジュール依存関係

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
- `n:codeSelect` はカスタムタグライブラリの一部。JavaScriptのインラインスクリプトを `n:codeSelect` が生成する要素に直接指定しないこと（Content-Security-Policy対策）。
- カスタムタグは言語指定によるコード値の取得に対応していない。言語指定でコード値を取得したい場合は、アクションで `CodeUtil` を使用すること。
- パターンを使用して選択値を制限した場合、バリデーションも同パターンの `@CodeValue` アノテーションで対応すること。
- ドメインバリデーションを使用する場合、1つのドメインに対して1つのパターンしか指定できないため、複数パターンに対応するにはパターンごとにドメインを定義すること。

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-code.json#s2`, `component/libraries/libraries-tag_reference.json#s4`, `component/libraries/libraries-tag_reference.json#s6`, `component/libraries/libraries-code.json#s5`, `component/libraries/libraries-code.json#s6`
