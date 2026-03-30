
**結論**: コード値のプルダウン入力には `n:codeSelect` カスタムタグを使用します。DBに登録されたコード値を自動的に選択肢として表示でき、確認画面では自動的に `<div>` 要素で表示が切り替わります。

**根拠**:

コード値専用プルダウンタグ `n:codeSelect` の使用方法:

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
<!-- 入力画面: <select>要素で出力、確認画面: <div>要素で出力 -->
```

主要属性:

| 属性名 | 必須 | デフォルト値 | 説明 |
|---|---|---|---|
| name | ○ | | XHTMLのname属性 |
| codeId | ○ | | コードID（DBに登録されたコードのID） |
| pattern | | 指定なし | 使用するパターンのカラム名 |
| optionColumnName | | | 取得するオプション名称のカラム名 |
| labelPattern | | `$NAME$` | ラベル整形パターン。`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値） |
| listFormat | | `br` | 出力フォーマット（`br`/`div`/`span`/`ul`/`ol`/`sp`） |

コード値専用カスタムタグ一覧（参考）:
- `n:code` : コード値表示
- `n:codeSelect` : コード値のプルダウン
- `n:codeCheckbox` : コード値のチェックボックス
- `n:codeRadioButtons` : コード値の複数のラジオボタン
- `n:codeCheckboxes` : コード値の複数のチェックボックス

なお、一般的な選択肢リスト（DB等から取得したカスタムリスト）のプルダウンには `n:select` を使用します。その場合はアクション側でリストをリクエストスコープに設定する必要があります:

```java
// アクション: リクエストスコープに選択肢リストを設定
EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
context.setRequestScopedVar("industries", industries);
```

```jsp
<%-- JSP: n:select でプルダウンを表示 --%>
<n:select
    listName="industries"
    elementValueProperty="industryCode"
    elementLabelProperty="industryName"
    name="form.industry"
    withNoneOption="true" />
```

**注意点**:
- `n:codeSelect` は `CodeUtil` のロケールを指定しないAPIを使用しているため、**言語指定によるコード値の取得はできない**。言語指定でコード値を取得したい場合は、アクションで `CodeUtil` を直接使用すること。
- `n:select` の選択状態判定は、選択された値と選択肢の値をともに `Object#toString` してから行う。
- カスタムタグはSPA（シングルページアプリケーション）には対応していない。

参照: `component/libraries/libraries-tag.json#s1`, `component/libraries/libraries-tag_reference.json#s5`
