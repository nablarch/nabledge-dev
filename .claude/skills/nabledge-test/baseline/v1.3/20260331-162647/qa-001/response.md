**結論**: コードリストのプルダウン入力を実装するには、JSPで `n:codeSelect` タグを使用します。このタグはHTMLの `<select>` タグに対応し、コード管理機能（CODE_PATTERNテーブル・CODE_NAMEテーブル）から選択肢を自動生成します。

---

**根拠**:

## 基本的な使い方

```jsp
<n:codeSelect name="batch.status"
              codeId="0002" pattern="PATTERN1"
              labelPattern="$NAME$" />
```

| 属性 | 必須 | 説明 |
|---|---|---|
| `name` | ○ | フォームのname属性（リクエストパラメータ名） |
| `codeId` | ○ | コードID（CODE_PATTERNテーブルのID） |
| `pattern` | | CODE_PATTERNテーブルのどのカラムで絞り込むかを指定 |
| `labelPattern` | | 選択肢のラベル書式（デフォルト: `$NAME$`） |
| `withNoneOption` | | `true` でリスト先頭に「選択なし」を追加（デフォルト: `false`） |
| `noneOptionLabel` | | 選択なしオプションのラベル |
| `optionColumnName` | | `$OPTIONALNAME$` 使用時のオプション名称カラム名 |

## 選択肢の絞り込みロジック

CODE_NAMEテーブルのうち、以下の条件を満たす行が選択肢になります：
1. `codeId` 属性で指定したID
2. CODE_PATTERNテーブルの `pattern` 属性で指定したカラムの値が `1`

## labelPatternのプレースホルダ

| プレースホルダ | 内容 |
|---|---|
| `$VALUE$` | コード値（VALUEカラム） |
| `$NAME$` | コード名称（NAMEカラム） |
| `$SHORTNAME$` | コード略称（SHORT_NAMEカラム） |
| `$OPTIONALNAME$` | オプション名称（`optionColumnName` 属性の指定が必須） |

## 実装例（入力画面）

**JSP**:
```jsp
<n:codeSelect name="batch.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

**HTML出力（入力画面）**:
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

**HTML出力（確認画面）**:
```html
<div>03:処理実行中-実行-0002-03-ja</div>
```

## Actionクラスでの初期値設定

入力/更新画面で初期値を表示するには、JSP遷移前にActionクラスでリクエストスコープにデータを設定します。カスタムタグの `name` 属性と設定名を一致させてください。

```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03"); // "03"を設定
context.setRequestScopedVar("batch", batch);
```

---

**注意点**:
- `listFormat` 属性はcodeSelectタグでは**確認画面のみ**適用されます（入力画面には適用されません）
- `$OPTIONALNAME$` プレースホルダを使用する場合は、`optionColumnName` 属性でカラム名を必ず指定してください
- 確認画面の実装には `n:confirmationPage` タグを使用して入力画面にフォワードします
- コード値の一覧をテキストボックスで入力する仕様の場合は、別途 `list-of-codes-searched-by-codeId-and-pattern` の実装を参照してください

参照: `guide/web-application/web-application-inputAndOutput.json#s3`, `component/libraries/libraries-07_TagReference.json#s14`, `component/libraries/libraries-07_DisplayTag.json#s2`
