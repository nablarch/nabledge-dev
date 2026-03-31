**結論**: コードリストのプルダウン入力を実装するには、JSPで `n:codeSelect` タグを使用し、`codeId` 属性にコードIDを指定します。

**根拠**:

## 基本的な実装方法

`n:codeSelect` タグは `<select>` タグに対応し、CODE_PATTERNテーブルとCODE_NAMEテーブルからコード値リストを取得してプルダウンを生成します。

**JSP実装例（最小構成）**:
```jsp
<n:codeSelect name="form.codeValue" codeId="codeId" />
```

**属性指定の詳細例**:
```jsp
<n:codeSelect name="W11AF01.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

## 主要属性

| 属性 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | XHTMLのname属性 |
| codeId | ○ | | コードID |
| pattern | | （指定なし） | 使用するパターンのカラム名（例: `PATTERN2`）。CODE_PATTERNテーブルのうち、指定カラムの値が1の行から選択肢を作成する |
| optionColumnName | | | 取得するオプション名称のカラム名 |
| labelPattern | | `$NAME$` | ラベル整形パターン。プレースホルダ: `$NAME$`（コード名称）/ `$SHORTNAME$`（略称）/ `$OPTIONALNAME$`（オプション名称）/ `$VALUE$`（コード値） |
| withNoneOption | | `false` | `true` にするとリスト先頭に選択なしオプションを追加 |
| noneOptionLabel | | （空文字） | 選択なしオプションのラベル（`withNoneOption="true"` の場合のみ有効） |
| errorCss | | `nablarch_error` | エラー時のCSSクラス名 |

## 画面出力例

**アクションの実装（リクエストスコープへの値設定）**:
```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03");
context.setRequestScopedVar("batch", batch);
```

**JSP**:
```jsp
<n:codeSelect name="batch.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**入力画面のHTML出力**:
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

**確認画面のHTML出力**:
```html
<div>03:処理実行中-実行-0002-03-ja</div>
```

## CodeUtilによるコード値取得（Java側での利用）

JavaコードでコードIDに対応するコード値リストを取得したい場合は `CodeUtil.getValues()` を使用します:

```java
// コードIDに対応するコード値一覧を取得する
List<CodeItem> codeItems = CodeUtil.getValues("codeId");
```

**注意点**:

- `listFormat` 属性は `n:codeSelect` タグでは確認画面用出力時のみ適用されます（入力画面では通常のselectタグが出力されます）。
- 確認画面では `confirmationPage` タグを使い入力画面にフォワードすることで、入力画面と確認画面をJSP共通化できます。
- SORT_ORDERは言語（`lang`）ごとに異なる場合があるため、多言語環境では表示順が言語によって変わることに注意してください。

参照: `guide/web-application/web-application-Other.json#s8`, `guide/web-application/web-application-inputAndOutput.json#s2`, `component/libraries/libraries-07_TagReference.json#s14`