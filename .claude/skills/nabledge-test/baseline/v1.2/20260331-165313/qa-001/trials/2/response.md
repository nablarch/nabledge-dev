**結論**: コードリストのプルダウン入力を実装するには、JSPで `n:codeSelect` タグを使用し、`codeId` 属性にコードIDを指定します。

**根拠**:

## 基本的な実装方法

JSPで `n:codeSelect` タグを使用してプルダウン（selectタグ）を出力します。

```jsp
<%-- 基本的な使用例 --%>
<n:codeSelect name="form.codeValue" codeId="codeId" />
```

`n:codeSelect` タグは、CODE_PATTERNテーブルとCODE_NAMEテーブルのデータを使用して選択項目リストを生成します。

## 主要な属性

| 属性 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | 選択されたコード値を受け取るname属性 |
| codeId | ○ | | コードID（CODE_PATTERNテーブルのID） |
| pattern | | | 使用するパターンのカラム名（例: `PATTERN2`） |
| labelPattern | | `$NAME$` | ラベル整形パターン |
| optionColumnName | | | オプション名称のカラム名 |
| withNoneOption | | false | 先頭に「選択なし」を追加するか |
| noneOptionLabel | | `""` | 「選択なし」のラベル（withNoneOption="true"時のみ有効） |

## labelPatternのプレースホルダ

- `$VALUE$`: コード値（VALUE）
- `$NAME$`: コード名称（NAME）
- `$SHORTNAME$`: コード略称（SHORT_NAME）
- `$OPTIONALNAME$`: コードのオプション名称（OPTION01）※`optionColumnName` 指定が必要

## 具体的な実装例

Actionクラスでリクエストスコープに値を設定:
```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03"); // 初期選択値
context.setRequestScopedVar("batch", batch);
```

JSP:
```jsp
<n:codeSelect name="batch.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

入力画面HTML出力例:
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

確認画面では選択値がテキストとして出力されます:
```html
<div>03:処理実行中-実行-0002-03-ja</div>
```

## CodeUtilを使ったコード値取得（Java側）

Javaコードでコード値リストを取得する場合は `CodeUtil.getValues(codeId)` を使用します:

```java
List<CodeItem> codeItems = CodeUtil.getValues("codeId");
```

**注意点**:
- `pattern` 属性に指定したカラム名（例: `PATTERN2`）の値が `1` の行のみが選択項目リストに含まれます
- `withNoneOption="true"` を指定すると、リストの先頭に「選択なし」オプションが追加されます（デフォルトは追加しない）
- 確認画面と入力画面を共通化するには `confirmationPage` タグと組み合わせます
- `listFormat` 属性（`br`/`div`/`span`/`ul`/`ol`/`sp`）は、`codeSelect` タグの場合、確認画面用出力時のみ適用されます

参照: `guide/web-application/web-application-Other.json#s8`, `guide/web-application/web-application-inputAndOutput.json#s2`, `component/libraries/libraries-07_DisplayTag.json#s1`

###