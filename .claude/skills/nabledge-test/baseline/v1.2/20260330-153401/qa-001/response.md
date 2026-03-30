**結論**: コードリストのプルダウン入力を実装するには、JSPで `n:codeSelect` タグを使用し、`codeId` 属性にコードIDを指定します。

**根拠**:

## 基本的な実装方法

`n:codeSelect` タグを使用してHTMLの `<select>` タグを出力します。

```jsp
<n:codeSelect name="form.codeValue" codeId="codeId" />
```

## 主要属性

| 属性 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | 選択値のリクエストパラメータ名 |
| codeId | ○ | | コードID |
| pattern | | | 使用するパターンのカラム名 |
| labelPattern | | `$NAME$` | ラベル整形パターン |
| withNoneOption | | false | 先頭に「選択なし」を追加するか |

## 「選択なし」オプションの追加

```jsp
<n:select name="user.groupIds"
          listName="allGroups" elementLabelProperty="name" elementValueProperty="id"
          withNoneOption="true" noneOptionLabel="選択なし" />
```

## コード値をJavaで取得する場合

`CodeUtil.getValues(codeId)` でコードIDに対応するコード値リストを取得できます:

```java
List<CodeItem> codeItems = CodeUtil.getValues("codeId");
```

**注意点**:
- `pattern` 属性には CODE_PATTERN テーブルのカラム名を指定します。

参照: `guide/web-application/web-application-Other.json#s8`, `component/libraries/libraries-07_DisplayTag.json#s1`
