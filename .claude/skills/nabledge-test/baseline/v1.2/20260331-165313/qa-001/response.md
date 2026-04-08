**結論**: コードリストのプルダウン入力を実装するには、JSPで `<n:codeSelect>` タグを使用します。`codeId` 属性にコードIDを指定するだけで、CODE_PATTERNテーブルとCODE_NAMEテーブルから選択項目リストを自動取得してselectタグを生成します。

---

**根拠**:

### 基本的な使い方

JSPに以下のように記述します：

```jsp
<n:codeSelect name="form.status" codeId="0002" />
```

- `name`: フォームのプロパティ名（リクエストパラメータ名）
- `codeId`: 使用するコードID（必須）

### 主な属性

| 属性 | 必須 | デフォルト | 説明 |
|---|---|---|---|
| name | ○ | | XHTMLのname属性 |
| codeId | ○ | | コードID |
| pattern | | （なし） | 使用するパターンのカラム名（例: `"PATTERN2"`）。指定したカラム値が"1"の行のみ選択肢にする |
| labelPattern | | `$NAME$` | ラベル表示パターン。`$VALUE$`（コード値）、`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）が使用可能 |
| optionColumnName | | | `$OPTIONALNAME$`を使う場合に取得するオプション名称のカラム名 |
| withNoneOption | | false | trueで先頭に「選択なし」オプションを追加 |
| noneOptionLabel | | （空文字） | 「選択なし」オプションのラベル |
| listFormat | | br | 確認画面表示時のフォーマット（br/div/span/ul/ol/sp）|

### 実装例（コード値＋名称の表示）

**Actionクラス**（初期値設定）：
```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03");
context.setRequestScopedVar("batch", batch);
```

**JSP**（詳細なlabelPattern指定例）：
```jsp
<n:codeSelect name="batch.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**入力画面 HTML 出力例**：
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

**確認画面 HTML 出力例**：
```html
<div>03:処理実行中-実行-0002-03-ja</div>
```

### コードリストをJavaから取得する場合

`CodeUtil.getValues()` を使ってコード値一覧を取得することもできます：

```java
// コードIDに対応するコード値一覧を取得する
List<String> values = CodeUtil.getValues("0002");

// パターンでフィルタしたコード値を取得する
List<String> values = CodeUtil.getValues("0002", "PATTERN1");
```

JSPでは `n:codeSelect` タグの `listId` 属性でも使用できます：

```jsp
<n:codeSelect name="form.codeValue" codeId="codeId" />
```

---

**注意点**:

1. **pattern属性**: CODE_PATTERNテーブルの指定カラム値が`1`の行のみが選択肢になります。未指定の場合は全コード値が対象です。
2. **$OPTIONALNAME$使用時**: `optionColumnName` 属性でオプション名称カラム名を指定する必要があります。指定がないと`$OPTIONALNAME$`は表示されません。
3. **listFormat属性の適用範囲**: `codeSelect`タグでは確認画面用出力時のみ適用されます（入力画面のselectタグには影響しません）。
4. **コード値バリデーション**: Formクラスのsetterに`@CodeValue(codeId="0001", pattern="PATTERN1")`アノテーションを付与することで、選択値がコードリストに含まれるかバリデーションできます。

---

参照: `guide/web-application/web-application-inputAndOutput.json#s2`, `component/libraries/libraries-07_TagReference.json#s14`, `guide/web-application/web-application-Other.json#s8`, `component/libraries/libraries-07_DisplayTag.json#s1`

###