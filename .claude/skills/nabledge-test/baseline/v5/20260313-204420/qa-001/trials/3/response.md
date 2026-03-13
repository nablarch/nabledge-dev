**結論**: Nablarch 5 でコード値のプルダウン入力を実装するには、2つのアプローチがあります。(1) コード管理機能を使う場合は `n:codeSelect` タグを使用する。(2) 任意リストを使う場合は `n:select` タグとアクション側でのリクエストスコープ設定を組み合わせる。

---

**根拠**:

### アプローチ1: コード管理機能を使ったプルダウン（`n:codeSelect`）

コードマスタに登録済みのコード値をプルダウンで表示する場合は `n:codeSelect` タグを使用します。

**JSP実装例**:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```
- 入力画面では `<select>` タグが生成される
- 確認画面では選択値のテキストが出力される（入力・確認画面のJSP共通化が可能）

**主要属性**（`n:codeSelect`）:

| 属性名 | 必須 | 説明 |
|---|---|---|
| `codeId` | ◎ 必須 | コード定義ID（コードマスタのID） |
| `pattern` | ○ 任意 | 使用するコードパターンのカラム名（デフォルト: PATTERN01） |
| `optionColumnName` | ○ 任意 | オプション名称カラム名（デフォルト: OPTION01） |
| `labelPattern` | ○ 任意 | ラベル表示書式。プレースホルダ: `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$VALUE$`（コード値）。デフォルト: `$NAME$` |
| `withNoneOption` | ○ 任意 | リスト先頭に「選択なし」オプションを追加するか（デフォルト: false） |

---

### アプローチ2: 任意リストを使ったプルダウン（`n:select`）

DBやロジックから取得した任意のリストをプルダウン表示する場合は `n:select` タグを使用します。

**アクション実装例**:
```java
public HttpResponse input(HttpRequest request, ExecutionContext context) {
    EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
    context.setRequestScopedVar("industries", industries);
    return new HttpResponse("/WEB-INF/view/client/create.jsp");
}
```

**JSP実装例**:
```jsp
<n:select
    listName="industries"
    elementValueProperty="industryCode"
    elementLabelProperty="industryName"
    name="form.industryCode"
    withNoneOption="true"
    cssClass="btn dropdown-toggle"/>
```

**主要属性**（`n:select`）:

| 属性名 | 説明 |
|---|---|
| `listName` | リクエストスコープの選択肢リスト名 |
| `elementValueProperty` | 値を表すプロパティ名 |
| `elementLabelProperty` | ラベルを表すプロパティ名 |
| `withNoneOption` | リスト先頭に「選択なし」を追加するか |

**出力されるHTML例**（`form.plan1` の値が `"A"` の場合）:
```html
<select name="form.plan1">
  <option value="A" selected="selected">フリー</option>
  <option value="B">ベーシック</option>
  <option value="C">プレミアム</option>
</select>
```

---

**注意点**:
- `listName` に空のリストをセットした場合、プルダウンには何も出力されない（Nablarch 5u14 でドキュメントに明記された仕様）
- カスタムタグはJavaScriptが必須。GETリクエストでは一部のカスタムタグが使用できない制限がある
- コード値を言語指定で取得する場合は、カスタムタグでは不可。アクション側で `CodeUtil` のロケール指定APIを使用すること
- `n:codeSelect` の `codeId` は必須属性であり、未指定の場合は動作しない

参照: `component/libraries/libraries-tag.json#s1`, `processing-pattern/web-application/web-application-client_create1.json#s1`, `development-tools/testing-framework/testing-framework-field_code_pulldown.json#s2`