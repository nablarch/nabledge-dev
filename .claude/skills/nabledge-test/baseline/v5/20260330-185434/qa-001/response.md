
**結論**: コード値のプルダウン入力を実装するには、`n:codeSelect` カスタムタグを使用し、`codeId` 属性にコードIDを指定します。一般的なリストからのプルダウンには `n:select` タグも使用できます。

---

**根拠**:

#### コード値のプルダウン（`n:codeSelect`）

[コード管理機能](component/libraries/libraries-code.json#s1) から取得したコード値を表示するカスタムタグ `n:codeSelect` を使用します。

**主要属性**:
- `codeId`: コードID（必須）
- `pattern`: 使用するパターンのカラム名（デフォルト: 指定なし）
- `optionColumnName`: オプション名称のカラム名
- `labelPattern`: ラベル整形パターン。プレースホルダ: `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）、`$VALUE$`（コード値）。デフォルト: `$NAME$`

**JSP実装例**:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```

- 入力画面では `<select>` タグとして出力されます
- 確認画面では選択値のテキストとして出力されます（例: `<div>FEMALE-女</div>`）

---

#### 任意リストからのプルダウン（`n:select`）

コード管理機能を使わず、業務データからプルダウンを作成する場合は `n:select` タグを使用します。

**アクション側**: UniversalDao でデータを全件取得し、リクエストスコープに設定します。

```java
public HttpResponse input(HttpRequest request, ExecutionContext context) {
    EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
    context.setRequestScopedVar("industries", industries);
    return new HttpResponse("/WEB-INF/view/client/create.jsp");
}
```

**JSP側**: `listName` にリクエストスコープの変数名を指定します。

```jsp
<n:select
    listName="industries"
    elementValueProperty="industryCode"
    elementLabelProperty="industryName"
    name="form.industryCode"
    withNoneOption="true"
    cssClass="btn dropdown-toggle" />
```

**カスタムタグの属性**:
- `listName`: 選択肢リストのリクエストスコープ変数名
- `elementLabelProperty`: ラベルを表すプロパティ名
- `elementValueProperty`: 値を表すプロパティ名
- `withNoneOption`: `true` にするとリスト先頭に「選択なし」オプションを追加

---

**注意点**:
- カスタムタグを使用するには、JSP 2.1以降をサポートするWebコンテナが必要です
- カスタムタグはクライアント側のJavaScriptが必須です
- 言語指定によるコード値取得はカスタムタグでは不可。言語指定が必要な場合はアクションで `CodeUtil` を使用してください
- 選択状態の判定は、選択された値と選択肢の値をともに `Object#toString` してから行います

参照: `component/libraries/libraries-tag.json#s1`, `processing-pattern/web-application/web-application-client_create1.json#s1`
