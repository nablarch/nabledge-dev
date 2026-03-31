**結論**: コードリストのプルダウン入力は、JSPで `n:codeSelect` タグを使用し、`codeId` 属性にコードIDを指定することで実装できます。

**根拠**:

`n:codeSelect` タグは HTML の `<select>` タグに対応し、CODE_PATTERN テーブルと CODE_NAME テーブルからコード値一覧を取得してプルダウンを生成します。

**基本的なJSP実装例**:
```jsp
<n:codeSelect name="form.codeValue" codeId="codeId" />
```

**属性指定ありの例**（PATTERN2 でフィルタリング、ラベルにコード値・名称・略称・オプション名称を表示）:
```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**主な属性**:

| 属性 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | 選択されたコード値を取得するname属性 |
| codeId | ○ | | コードID（CODE_PATTERNテーブル・CODE_NAMEテーブルのID） |
| pattern | | 指定なし | 使用するパターンのカラム名（例: `PATTERN2`） |
| optionColumnName | | | 取得するオプション名称のカラム名 |
| labelPattern | | `$NAME$` | ラベル整形パターン（`$VALUE$`/`$NAME$`/`$SHORTNAME$`/`$OPTIONALNAME$`） |
| withNoneOption | | false | `true` で先頭に「選択なし」オプションを追加 |
| noneOptionLabel | | `""` | 「選択なし」のラベル（`withNoneOption="true"` の場合のみ有効） |

**アクションクラス実装例**:
```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03"); // 初期選択値を設定
context.setRequestScopedVar("batch", batch);
```

**JSP（入力画面）出力例**:
```html
<select name="batch.status">
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

**確認画面（`n:confirmationPage` タグとの共通JSP）**:
確認画面では `n:codeSelect` タグが選択値をテキスト形式で出力します（`listFormat` 属性で形式指定）:
```html
<div>03:処理実行中-実行-0002-03-ja</div>
```

**注意点**:
- `pattern` 属性を指定すると、CODE_PATTERN テーブルの該当カラムの値が `1` の行のみがプルダウンの選択肢として表示されます。
- `$OPTIONALNAME$` プレースホルダを使用する場合は `optionColumnName` 属性の指定が必須です。
- CODE_NAME テーブルの SORT_ORDER は言語ごとに異なる場合があるため、多言語環境では表示順が変わることに注意してください。
- `CodeUtil.getValues(codeId)` を使用してコード値リストを Java コードで取得することも可能です。

参照: `component/libraries/libraries-07_DisplayTag.json#s1`, `guide/web-application/web-application-Other.json#s8`, `guide/web-application/web-application-inputAndOutput.json#s2`