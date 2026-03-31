**結論**: コードリストのプルダウン入力を実装するには、JSPで `<n:codeSelect>` タグを使用します。`codeId` 属性にコードIDを指定することで、CODE_PATTERN・CODE_NAMEテーブルから選択項目を自動的に取得してHTMLの `<select>` タグとして出力されます。

**根拠**:

**JSP実装例**:
```jsp
<n:codeSelect name="batch.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**出力HTML（入力画面）**:
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

**主な属性**:

| 属性 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | リクエストパラメータ/変数スコープのプロパティ名 |
| codeId | ○ | | コードID（CODE_PATTERNテーブルのID） |
| pattern | | 指定なし | 使用するパターンのカラム名（例: `PATTERN2`） |
| optionColumnName | | | 取得するオプション名称のカラム名（例: `OPTION01`） |
| labelPattern | | `$NAME$` | ラベル表示書式。プレースホルダ: `$VALUE$`（コード値）、`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称） |
| withNoneOption | | `false` | `true` にするとリスト先頭に「選択なし」オプションを追加 |
| noneOptionLabel | | `""` | 選択なしのラベル文字列。`withNoneOption="true"` の場合のみ有効 |
| listFormat | | `br` | 確認画面用出力のフォーマット（br/div/span/ul/ol/sp） |

**Actionクラスの実装例**:
```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03");
context.setRequestScopedVar("batch", batch);
```

**確認画面対応**: 確認画面に `confirmationPage` タグを使ってフォワードすることで、選択したコード値のラベルがテキスト表示されます。

**注意点**:

1. **CODE_PATTERNテーブル・CODE_NAMEテーブルが必要**: `n:codeSelect` はDBのCODE_PATTERNテーブルとCODE_NAMEテーブルを参照するため、これらのテーブルにデータが登録されていることが前提です。

2. **コード値バリデーション**: 入力されたコード値が有効かどうかを検証するには、`@CodeValue` アノテーションと `CodeValidationUtil.validate()` を使用します。`CodeValidationUtil` はサンプル実装のため、プロジェクトで取り込みが必要です。
   ```java
   @CodeValue(codeId="0001")
   public String setGender(String gender) { ... }
   ```

3. **`n:codeSelect` vs `n:select` の使い分け**: コード管理テーブルから選択肢を取得する場合は `n:codeSelect`、List型変数から選択肢を生成する場合は `n:select` を使用します。

4. **ローカル動作（UIフレームワーク使用時）**: UIフレームワークの `field_code_pulldown` ウィジェットを使う場合、ローカル動作時は `/js/devtool/resource/コード値定義.js` から選択肢を取得します。`codeId` と `sample` を両方指定した場合は `sample` が優先されます。

参照: `component/libraries/libraries-07_DisplayTag.json#s1`, `guide/web-application/web-application-inputAndOutput.json#s3`, `guide/web-application/web-application-inputAndOutput.json#s2`, `component/ui-framework/ui-framework-field_code_pulldown.json#s2`, `guide/web-application/web-application-Validation.json#s3`