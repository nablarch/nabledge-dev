**結論**: コード値のプルダウン入力を実装するには、`n:codeSelect` カスタムタグを使用します。コードIDを `codeId` 属性に指定するだけで、コードマスタから自動的に選択肢を取得してプルダウンを描画できます。

**根拠**:

## 基本実装

JSPで `n:codeSelect` タグを使用します。

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" />
```

- 入力画面では `<select>` 要素を出力
- 確認画面では選択されたコード値のラベルをテキストで出力（入力・確認画面JSPを共通化可能）

## 主要属性

| 属性 | 必須 | デフォルト | 説明 |
|---|---|---|---|
| `name` | ○ | | XHTMLのname属性 |
| `codeId` | ○ | | コードID（コードマスタのID） |
| `pattern` | | 指定なし | 使用するパターンのカラム名 |
| `optionColumnName` | | | オプション名称のカラム名 |
| `labelPattern` | | `$NAME$` | ラベル整形パターン。`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$VALUE$`（コード値）、`$OPTIONALNAME$`（オプション名称）が使用可能 |
| `listFormat` | | `br` | リスト表示フォーマット（`div`/`span`/`ul`/`ol`/`sp`） |

## パターン指定の例（機能ごとに表示するコードを切り替える）

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
```

コードパターンテーブルのパターンカラム（`PATTERN2` 等）で表示・非表示を切り替えられます。パターン名は設定ファイルで設定したカラム名と**厳密に一致**させる必要があります。

## ラベル整形の例

```jsp
<n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2"
              labelPattern="$VALUE$-$SHORTNAME$" listFormat="div" />
<!-- 入力画面: <select name="form.gender">
       <option value="MALE">MALE-男</option>
       <option value="FEMALE" selected="selected">FEMALE-女</option>
     </select> -->
<!-- 確認画面: <div>FEMALE-女</div> -->
```

## 必要モジュール（Maven依存関係）

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-code</artifactId>
</dependency>
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-common-code-jdbc</artifactId>
</dependency>
```

**注意点**:
- `n:codeSelect` カスタムタグでは**言語指定によるコード値取得は不可**。`CodeUtil` のロケール未指定APIを使用しているため、言語指定が必要な場合はアクションで `CodeUtil` を使用すること。
- コードマスタを使わない一般的なプルダウン（任意リスト）には `n:select` タグを使用する。その場合はアクションで選択肢リストをリクエストスコープに設定し、`listName`/`elementLabelProperty`/`elementValueProperty` 属性で指定する。
- `pattern` 属性のパターン名は設定ファイルのカラム名と厳密に一致させること。

参照: `component/libraries/libraries-tag.json#s1`、`component/libraries/libraries-tag_reference.json#s5`、`component/libraries/libraries-code.json#s2`