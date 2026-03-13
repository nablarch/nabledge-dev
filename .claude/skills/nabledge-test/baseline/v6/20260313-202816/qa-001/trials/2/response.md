**結論**: コード値のプルダウン入力を実装するには、`n:codeSelect` タグ（コード値専用）または `n:select` タグ（任意リストから）を使用します。コード値を使用する場合は `n:codeSelect` が推奨です。

---

**根拠**:

## 方法1: コード値専用タグ `n:codeSelect` を使用する（推奨）

コード管理機能のコード値からプルダウンを生成する場合は `n:codeSelect` タグを使用します。

**JSP実装例**:
```jsp
<n:codeSelect name="form.gender"
              codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$"
              listFormat="div" />
```

- 入力画面では `<select>` 要素で出力され、確認画面では `<div>` 要素で出力されます（入力/確認画面の共通化に対応）。

**主な属性**:

| 属性名 | 必須 | 説明 |
|---|---|---|
| name | ○ | フォームのプロパティ名 |
| codeId | ○ | コードID |
| pattern | | 使用するパターンのカラム名（デフォルト: 指定なし） |
| labelPattern | | ラベル整形パターン（`$NAME$`, `$SHORTNAME$`, `$VALUE$`, `$OPTIONALNAME$`） |
| optionColumnName | | 取得するオプション名称のカラム名 |
| listFormat | | 出力フォーマット（`br`/`div`/`span`/`ul`/`ol`/`sp`） |

アクション側での特別な準備は不要です（コード管理機能が自動的にコードリストを提供します）。

---

## 方法2: 任意リストから `n:select` タグを使用する

DBなどから取得した任意の選択肢リストでプルダウンを作成する場合は `n:select` タグを使用します。

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
    cssClass="form-select form-select-lg"/>
```

**出力されるHTML**（例: `form.plan1` の値が "A" の場合）:
```html
<select name="form.plan1">
  <option value="A" selected="selected">フリー</option>
  <option value="B">ベーシック</option>
  <option value="C">プレミアム</option>
</select>
```

**主な属性**:

| 属性 | 必須 | 説明 |
|---|---|---|
| name | ○ | XHTMLのname属性 |
| listName | ○ | 選択肢リストの名前（リクエストスコープから取得） |
| elementLabelProperty | ○ | ラベルを取得するプロパティ名 |
| elementValueProperty | ○ | 値を取得するプロパティ名 |

---

## コード値バリデーション

コード値プルダウンの入力値バリデーションには `@CodeValue` アノテーションを使用します。

**Bean Validation**:
```java
@CodeValue(codeId = "GENDER")
private String gender;
```

パターンを使って選択値を制限している場合は `pattern` 属性も指定します:
```java
@CodeValue(codeId = "GENDER", pattern = "PATTERN2")
private String gender;
```

**Nablarch Validation**:
```java
@CodeValue(codeId = "GENDER")
public void setGender(String gender) {
    this.gender = gender;
}
```

---

**注意点**:

- `n:codeSelect` タグはコード管理機能（`nablarch-common-code` モジュール）が必要です。Nablarch Validationで `@CodeValue` を使う場合も同モジュールが必要です。
- カスタムタグでは**言語指定によるコード値の取得ができません**。`n:codeSelect` は `CodeUtil` のロケールを指定しないAPIを使用しています。言語指定でコード値を取得したい場合はアクションで `CodeUtil` を使用してください。
- 選択状態の判定は、選択された値と選択肢の値をともに `Object#toString` してから行います。
- カスタムタグはSPA（シングルページアプリケーション）に対応していません。

参照: `libraries-tag.json#s1`, `processing-pattern/web-application/web-application-client_create1.json#s1`, `libraries-code.json#s6`, `libraries-nablarch_validation.json#s2`
