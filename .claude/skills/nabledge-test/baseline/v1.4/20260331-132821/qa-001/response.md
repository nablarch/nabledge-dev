**結論**: コードリストのプルダウン入力には `n:codeSelect` タグ（codeSelectタグ）を使用します。`codeId` 属性でコードIDを指定すると、CODE_PATTERNテーブルとCODE_NAMEテーブルから選択項目リストを自動取得してHTMLのselectタグを出力します。

---

**根拠**:

**基本実装例（JSP）**:
```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**主要属性**:

| 属性名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | XHTMLのname属性 |
| codeId | ○ | | コードID（CODE_PATTERNテーブルのID） |
| pattern | | 指定なし | 使用するパターンのカラム名 |
| optionColumnName | | | 取得するオプション名称のカラム名 |
| labelPattern | | `$NAME$` | ラベル整形パターン。プレースホルダ: `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値） |
| withNoneOption | | false | リスト先頭に選択なしのオプションを追加するか否か |
| noneOptionLabel | | `""` | 選択なしオプションのラベル（withNoneOption="true"時のみ有効） |
| listFormat | | br | 確認画面用リスト表示フォーマット（br/div/span/ul/ol/sp） |

**アクション実装例**:
```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03"); // 初期値を設定
context.setRequestScopedVar("batch", batch);
```

**出力HTML（入力画面）**:
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

---

**参照**:
- `guide/web-application/web-application-inputAndOutput.json#s3`
- `component/libraries/libraries-07_TagReference.json#s14`
- `component/libraries/libraries-07_DisplayTag.json#s1`
- `component/ui-framework/ui-framework-field_code_pulldown.json#s2`
