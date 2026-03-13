**結論**: コード値のプルダウン入力を実装するには、JSPで `<n:codeSelect>` タグ（コード管理機能と連携）または `<n:select>` タグ（任意のリストを使用）を使用します。コード管理機能を使う場合は `codeId` 属性にコードIDを指定するだけでプルダウンを生成できます。

**根拠**:

### 方法1: コード管理機能を使った `n:codeSelect` タグ（コード値専用）

JSPでコード値のプルダウンを生成する場合は `n:codeSelect` タグを使用します。アクション側での事前処理は不要で、`codeId` を指定するだけでコード管理テーブルから選択肢を取得します。

```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

| 属性名 | 必須 | 説明 |
|---|---|---|
| name | ○ | XHTMLのname属性 |
| codeId | ○ | コードID |
| pattern | | 使用するパターンのカラム名 |
| optionColumnName | | 取得するオプション名称のカラム名 |
| labelPattern | | ラベル整形パターン（`$NAME$`=コード名称、`$SHORTNAME$`=略称、`$VALUE$`=コード値）。デフォルト: `$NAME$` |
| listFormat | | リスト表示フォーマット（br/div/span/ul/ol/sp） |

- 入力画面では `<select>` 要素で出力され、確認画面では `<div>` 要素で出力されます

この機能を使用するには、事前にコード管理機能の初期設定（`BasicCodeManager`, `BasicCodeLoader`, `BasicStaticDataCache` のコンポーネント定義）が必要です。

### 方法2: `n:select` タグ（任意リストを使用する汎用プルダウン）

業種リストなどDBのマスタデータを使ったプルダウンには `n:select` タグを使用します。アクション側でリクエストスコープに選択肢リストをセットし、JSPで参照します。

**アクション実装（リスト取得・リクエストスコープ設定）**:
```java
public HttpResponse input(HttpRequest request, ExecutionContext context) {
    EntityList<Industry> industries = UniversalDao.findAll(Industry.class);
    context.setRequestScopedVar("industries", industries);
    return new HttpResponse("/WEB-INF/view/client/create.jsp");
}
```

**JSP実装**:
```jsp
<n:select
    listName="industries"
    elementValueProperty="industryCode"
    elementLabelProperty="industryName"
    name="form.industryCode"
    withNoneOption="true"
    cssClass="form-select form-select-lg"
    errorCss="input-error" />
```

| 属性名 | 必須 | 説明 |
|---|---|---|
| name | ○ | XHTMLのname属性 |
| listName | ○ | 選択肢リストの名前（リクエストスコープから取得） |
| elementLabelProperty | ○ | リスト要素からラベルを取得するプロパティ名 |
| elementValueProperty | ○ | リスト要素から値を取得するプロパティ名 |

**バリデーション設定（プルダウン向けメッセージ）**:

プルダウン項目に適した入力必須メッセージを設定する場合は `@Required` の `message` 属性を使用します。

```java
@Required(message = "{nablarch.core.validation.ee.Required.select.message}")
@Domain("industryCode")
private String industryCode;
```

**注意点**:
- `n:codeSelect` で言語指定によるコード値の取得はできません。言語指定が必要な場合はアクション側で `CodeUtil` を使用してください
- コード管理機能はDBの参照整合性制約を設定できないため、バリデーションには `code-validation` を使用してください
- コード管理機能は静的なコード情報（性別区分など）を対象とします。動的に変化する情報（商品コードなど）はマスタテーブルで管理し `n:select` タグを使用してください

参照: `component/libraries/libraries-tag.json#s1`, `processing-pattern/web-application/web-application-client_create1.json#s1`, `component/libraries/libraries-code.json#s1`, `component/libraries/libraries-tag_reference.json#s5`, `component/libraries/libraries-tag_reference.json#s8`
