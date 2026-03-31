**結論**: コードリストのプルダウン入力は `n:codeSelect` タグを使用して実装する。CODE_PATTERNテーブルとCODE_NAMEテーブルのコードIDとパターンを指定することで、選択項目リストを自動的に取得できる。

**根拠**:

#### 基本的な実装方法

JSPで `n:codeSelect` タグを使用する：

```jsp
<n:codeSelect name="form.status" codeId="0002" />
```

主要属性：

| 属性 | 必須 | 説明 |
|---|---|---|
| name | ○ | 選択されたコード値を格納するリクエストパラメータ名 |
| codeId | ○ | コードID（CODE_PATTERNテーブルおよびCODE_NAMEテーブルのIDに対応） |
| pattern | | 使用するパターンのカラム名（例: `PATTERN2`）。指定したカラムの値が"1"の行から選択項目リストを作成 |
| withNoneOption | | リスト先頭に「選択なし」オプションを追加するか。`true`: 追加、`false`: 追加しない（デフォルト） |
| noneOptionLabel | | 「選択なし」のラベル（`withNoneOption="true"`の場合のみ有効） |
| labelPattern | | ラベル整形パターン。プレースホルダ: `$VALUE$`（コード値）、`$NAME$`（コード名称）、`$SHORTNAME$`（略称）、`$OPTIONALNAME$`（オプション名称）。デフォルト: `$NAME$` |
| optionColumnName | | `$OPTIONALNAME$`使用時のカラム名 |

#### 具体的な実装例

```jsp
<n:codeSelect name="batch.status"
              codeId="0002" pattern="PATTERN2" optionColumnName="OPTION01"
              labelPattern="$VALUE$:$NAME$-$SHORTNAME$-$OPTIONALNAME$"
              listFormat="div" />
```

上記の入力画面HTML出力例：
```html
<select name="batch.status">
    <option value="">選択なし</option>
    <option value="03" selected="selected">03:処理実行中-実行-0002-03-ja</option>
    <option value="04">04:処理実行完了-完了-0002-04-ja</option>
</select>
```

確認画面HTML出力例：
```html
<div>03:処理実行中-実行-0002-03-ja</div>
```

#### コード値の取得（Actionクラス側）

Actionクラスでプルダウンの初期値をリクエストスコープに設定する：

```java
BatchEntity batch = new BatchEntity();
batch.setStatus("03"); // 初期選択値を設定
context.setRequestScopedVar("batch", batch);
```

コード値一覧をJavaで取得する場合は `CodeUtil` クラスを使用する：

```java
// コードIDに対応するコード値一覧を取得
List<CodeItem> codeItems = CodeUtil.getValues("0002");

// パターンでフィルタしたコード値取得
List<String> values = CodeUtil.getValues("0002", "PATTERN2");
```

**注意点**:
- `n:codeSelect` タグは CODE_PATTERNテーブルとCODE_NAMEテーブルを参照する。これらのテーブルにデータが登録されている必要がある
- `listFormat` 属性は `n:codeSelect` タグでは確認画面用出力時のみ適用される
- `$OPTIONALNAME$` プレースホルダを使用する場合は `optionColumnName` 属性の指定が必須
- コード値のバリデーションには `@CodeValue` アノテーション（Formクラスのsetterに付与）を使用する：

```java
@PropertyName("ステータス")
@CodeValue(codeId="0002", pattern="PATTERN2")
public void setStatus(String status) {
    this.status = status;
}
```

参照: `guide/web-application/web-application-Other.json#s8`, `guide/web-application/web-application-inputAndOutput.json#s2`, `component/libraries/libraries-07_DisplayTag.json#s1`

###