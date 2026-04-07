**結論**: コード値のプルダウン入力を実装するには、`n:codeSelect` カスタムタグ（またはシンプルなリストには `n:select`）を使用します。コード管理機能と連携する場合は `n:codeSelect` が適切です。

**根拠**:

#### 1. コード値プルダウン: `n:codeSelect` を使用する方法

`n:codeSelect` はNablarchの [code](component/libraries/libraries-code.json) 機能と連携し、コード管理テーブルからコード値を取得してプルダウンを表示します。

主要属性:
- `codeId`: コードID（必須）
- `pattern`: 使用するパターンのカラム名（デフォルト: 指定なし）
- `optionColumnName`: オプション名称のカラム名
- `labelPattern`: ラベル整形パターン（プレースホルダ: `$NAME$`、`$SHORTNAME$`、`$OPTIONALNAME$`、`$VALUE$`。デフォルト: `$NAME$`）
- `withNoneOption`: リスト先頭に選択なしオプションを追加するか（デフォルト: false）

JSP実装例:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```

出力されるHTML（入力画面の場合）:
```html
<select name="form.gender">
  <option value="MALE">MALE-男</option>
  <option value="FEMALE" selected="selected">FEMALE-女</option>
</select>
```

> **重要**: `n:codeSelect` は入力画面と確認画面でJSPを共通化できます。入力画面では `<select>` タグ、確認画面では `<div>` タグが出力されます。

> **重要**: カスタムタグでは言語指定によるコード値取得は不可。言語指定が必要な場合は、アクションで `CodeUtil` を使用してください。

#### 2. 任意のリストを使ったプルダウン: `n:select` を使用する方法

コード管理機能を使わず、DBから取得したエンティティリストからプルダウンを作る場合は `n:select` を使用します。

アクションで選択肢リストをDBから取得してリクエストスコープに設定:
```java
public HttpResponse input(HttpRequest request, ExecutionContext context) {
    EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
    context.setRequestScopedVar("industries", industries);
    return new HttpResponse("/WEB-INF/view/client/create.jsp");
}
```

JSP実装例:
```jsp
<n:select
    listName="industries"
    elementValueProperty="industryCode"
    elementLabelProperty="industryName"
    name="form.industryCode"
    withNoneOption="true"
    cssClass="btn dropdown-toggle"/>
```

カスタムタグの属性:
- `listName`: 選択肢リストの名前（リクエストスコープに設定したキー名）
- `elementLabelProperty`: ラベルを表すプロパティ名
- `elementValueProperty`: 値を表すプロパティ名
- `withNoneOption`: 先頭に「選択なし」オプションを追加するか

出力されるHTML（`form.industryCode` の値が `"A"` の場合）:
```html
<select name="form.industryCode">
  <option value=""></option>
  <option value="A" selected="selected">製造業</option>
  <option value="B">サービス業</option>
</select>
```

**注意点**:
- `n:codeSelect` / `n:select` などのカスタムタグはJSP 2.1以降をサポートするWebコンテナが必要です
- クライアントのJavaScriptが必須です
- GETリクエストで一部のカスタムタグが使用できない制約があります
- `n:select` の選択状態判定は、選択された値と選択肢の値をともに `Object#toString` した上で行います
- リッチな画面やSPA（シングルページアプリケーション）には対応していません

参照: `component/libraries/libraries-tag.json#s1`、`processing-pattern/web-application/web-application-client_create1.json#s1`