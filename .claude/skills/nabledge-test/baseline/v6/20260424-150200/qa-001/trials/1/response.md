**結論**: コード値のプルダウン入力には、Nablarchが提供する `n:codeSelect` カスタムタグを使用します。コード管理機能で管理しているコード値をプルダウン（HTMLの`<select>`要素）として出力できる専用タグです。`codeId` 属性（必須）でコードIDを指定し、必要に応じて `pattern` 属性や `labelPattern` 属性で表示内容を制御します。

**根拠**:

1. **基本的な実装例**（`libraries-tag.json#s30`）

JSP:
```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

出力されるHTML（入力画面）:
```html
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>
```

2. **主な属性**（`libraries-tag-reference.json#s51`）

| 属性 | 説明 |
|---|---|
| name（必須） | XHTMLのname属性 |
| codeId（必須） | コードID |
| pattern | 使用するパターンのカラム名（機能毎に表示パターンを切り替え可能） |
| optionColumnName | オプション名称のカラム名 |
| labelPattern | ラベル整形パターン。プレースホルダは `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値） |
| listFormat | リスト表示のフォーマット（br/div/span/ul/ol/sp） |
| withNoneOption | リスト先頭に「選択なし」オプションを追加するか（true/false、デフォルトfalse） |
| noneOptionLabel | 「選択なし」オプションのラベル |

3. **パターンによる表示項目の切り替え**（`libraries-code.json#s7`）

コードパターンテーブルに `PATTERN2` 列を定義してOTHERを非表示にするなど、機能毎に表示項目を切替えられます。
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

4. **オプション名称の表示**（`libraries-code.json#s10`）

コード名称テーブルに `KANA_NAME` などのオプション名称カラムを定義し、`optionColumnName` と `labelPattern="$OPTIONALNAME$"` で表示できます。
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" optionColumnName="KANA_NAME"
              cssClass="form-control" labelPattern="$OPTIONALNAME$"/>
```

5. **入力値のバリデーション**（`libraries-code.json#s11`）

入力値がコードの有効範囲内かをチェックするため、`@CodeValue` アノテーションを使用します。

Bean Validationの場合:
```java
@CodeValue(codeId = "GENDER")
private String gender;
```

パターン指定も可能:
```java
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

6. **プルダウン変更でサブミットを行う**（`libraries-tag.json#s16`）

onchange属性で指定したボタンのclickイベントを発火させます（CSP対応が必要な場合は外部スクリプトまたはnonce属性推奨）。

**注意点**:
- カスタムタグ（`n:codeSelect` 等）では**言語指定によるコード値の取得はできません**。CodeUtil がロケールを指定しないAPIを内部で使用しているため、言語指定が必要な場合はアクション側で `CodeUtil` を直接使用してください（`libraries-tag.json#s30`）。
- `labelPattern` で `$OPTIONALNAME$` を使用する場合、`optionColumnName` 属性の指定が必須です。
- コード値関連のバリデータを使用する場合は、`nablarch-common-code` 依存を追加する必要があります（`libraries-nablarch-validation.json#s5`）。
- コード管理機能を使う前提で、コードパターンテーブル・コード名称テーブルの整備と `CodePatternSchema.patternColumnNames` などの初期設定が必要です。
- 選択項目の汎用的なプルダウンには `n:select` タグ（コード管理を使わない場合）がありますが、コード値を扱う場合は `n:codeSelect` を使用してください（`libraries-tag.json#s9`）。

参照:
- component/libraries/libraries-tag.json#s30（カスタムタグでコード値を表示する・codeSelect実装例）
- component/libraries/libraries-tag-reference.json#s51（codeSelectタグ属性仕様）
- component/libraries/libraries-code.json#s7（パターンによる表示切替）
- component/libraries/libraries-code.json#s10（オプション名称の表示）
- component/libraries/libraries-code.json#s11（@CodeValueバリデーション）
- component/libraries/libraries-tag.json#s16（プルダウン変更でサブミット）
- component/libraries/libraries-tag.json#s9（汎用selectタグ）
