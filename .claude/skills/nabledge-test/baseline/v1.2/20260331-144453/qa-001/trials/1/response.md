**結論**: コードリストのプルダウン入力を実装するには、JSPで `n:codeSelect` タグを使用し、`codeId` 属性にコードIDを指定します。

**根拠**:

## 基本実装

`n:codeSelect` タグは HTML の `<select>` タグとして出力されます。`codeId` 属性に CODE_PATTERN テーブルと CODE_NAME テーブルのコードIDを指定します。

```jsp
<%-- 最小構成 --%>
<n:codeSelect name="form.codeValue" codeId="codeId" />
```

## 主要属性

`codeSelect` タグ（および関連タグ共通）の主要な属性：

| 属性 | 必須 | デフォルト | 説明 |
|---|---|---|---|
| `name` | ○ | | 選択値を格納するリクエストパラメータ名 |
| `codeId` | ○ | | コードID |
| `pattern` | | | 使用するパターンのカラム名（例: `PATTERN2`）。CODE_PATTERN テーブルのうち指定カラムが `1` の行から選択肢を作成 |
| `labelPattern` | | `$NAME$` | ラベル整形パターン（`$VALUE$`・`$NAME$`・`$SHORTNAME$`・`$OPTIONALNAME$`） |
| `optionColumnName` | | | オプション名称のカラム名（`$OPTIONALNAME$` 使用時は必須） |
| `withNoneOption` | | `false` | `true` にすると先頭に「選択なし」オプションを追加 |
| `noneOptionLabel` | | `""` | 「選択なし」のラベル（`withNoneOption="true"` のときのみ有効） |
| `listFormat` | | `br` | 確認画面での表示フォーマット（`div`・`span`・`ul` など） |

## アクションとJSPの実装例

**Actionクラス**:
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

**入力画面の HTML 出力例**:
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

**確認画面の HTML 出力例**:
```html
<div>03:処理実行中-実行-0002-03-ja</div>
```

## コード値の取得（Java コードで使用する場合）

プルダウン以外に、Java コードでコード値リストを取得するには `CodeUtil.getValues()` を使用します：

```java
// コードID配下の全コード値を取得（SORT_ORDER 昇順）
List<String> values = CodeUtil.getValues("0002");

// パターンでフィルタしたコード値を取得
List<String> values = CodeUtil.getValues("0001", "PATTERN1");
```

**注意点**:

- `pattern` 属性を省略するとすべてのコード値が選択肢になります。特定パターンの値のみ表示したい場合は明示的に指定してください。
- `SORT_ORDER` は言語ごとに異なる場合があります。多言語環境では言語によって表示順が変わります。
- `$OPTIONALNAME$` プレースホルダを `labelPattern` に使用する場合は `optionColumnName` 属性の指定が必須です。

参照: `guide/web-application/web-application-Other.json#s8`, `guide/web-application/web-application-inputAndOutput.json#s2`, `component/libraries/libraries-07_DisplayTag.json#s1`, `component/libraries/libraries-02_CodeManager.json#s10`