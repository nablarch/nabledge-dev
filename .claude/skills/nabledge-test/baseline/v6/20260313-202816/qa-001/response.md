**結論**: コード値のプルダウン入力には、`n:codeSelect` カスタムタグ（コードIDからデータを直接取得）または `n:select` カスタムタグ（アクションでリクエストスコープに設定したリストを使用）の2種類があります。コード管理機能と連携する場合は `n:codeSelect` を使用します。

**根拠**:

**方法1: コード値専用タグ `n:codeSelect` を使用する（コード管理機能と連携）**

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

- `codeId`: コードID（必須）
- `pattern`: 使用するパターンのカラム名（任意）
- `labelPattern`: ラベル整形パターン。プレースホルダ `$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$VALUE$`（コード値）を使用可能
- 入力画面では `<select>` 要素で出力、確認画面では `<div>` 要素で出力される

バリデーションには `@CodeValue` アノテーションを使用する：

```java
// Bean Validation
@CodeValue(codeId = "GENDER")
private String gender;

// パターンを使用して選択値を制限する場合
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

**方法2: `n:select` タグ＋アクションでリスト設定（任意のリスト）**

アクションでデータ取得とリクエストスコープ設定を行う：

```java
public HttpResponse input(HttpRequest request, ExecutionContext context) {
    EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
    context.setRequestScopedVar("industries", industries);
    return new HttpResponse("/WEB-INF/view/client/create.jsp");
}
```

JSPで `n:select` タグを使用する：

```jsp
<n:select
    listName="industries"
    elementValueProperty="industryCode"
    elementLabelProperty="industryName"
    name="form.industryCode"
    withNoneOption="true"
    cssClass="form-select form-select-lg"/>
```

- `listName`: リクエストスコープに登録した選択肢リストの名前（必須）
- `elementValueProperty`: リスト要素から値を取得するプロパティ名（必須）
- `elementLabelProperty`: リスト要素からラベルを取得するプロパティ名（必須）

**注意点**:
- カスタムタグはリッチな画面やSPA（シングルページアプリケーション）に対応していない
- コード値のプルダウンで言語指定によるコード値の取得はできない（カスタムタグは `CodeUtil` のロケール非指定APIを使用）。言語指定が必要な場合はアクション側で `CodeUtil` を使用すること
- `pattern` 属性でプルダウン表示を絞り込んだ場合、バリデーション時も同パターンで `@CodeValue(pattern = "PATTERN2")` を指定すること

参照: `component/libraries/libraries-tag.json#s1`, `processing-pattern/web-application/web-application-client_create1.json#s1`, `component/libraries/libraries-code.json#s6`
