**結論**: Nablarch 5 でコード値のプルダウン入力を実装するには、`n:codeSelect` カスタムタグ（コード管理機能連携）または `n:select` カスタムタグ（任意リスト）を使用します。

---

**根拠**:

### 方法1: コード管理機能と連携したプルダウン（`n:codeSelect`）

コードマスタに登録済みのコード値をプルダウン表示する場合は `n:codeSelect` を使用します。

**JSP実装例**:
```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
```

- 入力画面では `<select>` タグが出力される
- 確認画面では選択値のテキストが出力される（入力・確認画面JSP共通化に対応）

**主要属性**:

| 属性名 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | フォームのプロパティ名 |
| `codeId` | ○ | コードID（コードマスタのID） |
| `pattern` | | 使用するパターンのカラム名（デフォルト: 指定なし） |
| `optionColumnName` | | オプション名称のカラム名 |
| `labelPattern` | | ラベル書式。`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$VALUE$`（コード値）が使用可（デフォルト: `$NAME$`） |
| `withNoneOption` | | 先頭に「選択なし」オプションを追加するか（デフォルト: false） |

**注意**: カスタムタグでは言語指定によるコード値取得は不可。`CodeUtil` のロケール未指定APIを使用しているため。言語指定が必要な場合はアクションで `CodeUtil` を使用すること。

---

### 方法2: 任意リストを使ったプルダウン（`n:select`）

DBから取得した任意のリスト（エンティティのリスト等）をプルダウン表示する場合は `n:select` を使用します。

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
    cssClass="btn dropdown-toggle" />
```

**`n:select` 主要属性**:

| 属性名 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | フォームのプロパティ名 |
| `listName` | ○ | リクエストスコープに設定した選択肢リストの変数名 |
| `elementLabelProperty` | ○ | リスト要素からラベルを取得するプロパティ名 |
| `elementValueProperty` | ○ | リスト要素から値を取得するプロパティ名 |

**注意**: `listName` に空のリストをセットした場合、画面には何も出力されません（Nablarch 5u14でドキュメント明記の仕様）。

---

**注意点**:
- `n:codeSelect` はコード管理機能（`code` コンポーネント）の設定が必要です
- カスタムタグはクライアントのJavaScriptが必須です
- GETリクエストでは `n:select` は使用可能ですが、一部タグ（`n:checkbox`、`n:code_checkbox` など）に制限があります
- 選択状態の判定は、選択された値と選択肢の値をともに `Object#toString` してから行います

参照: `libraries-tag.json#s1`, `web-application-client_create1.json#s1`, `libraries-tag_reference.json#s8`