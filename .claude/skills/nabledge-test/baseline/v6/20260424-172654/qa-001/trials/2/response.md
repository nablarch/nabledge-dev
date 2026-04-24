**結論**: Nablarch 6 では、コード値のプルダウン入力は **`n:codeSelect` カスタムタグ** を使用して実装します。コードID（および必要に応じてパターン名）を指定するだけで、コード管理機能から取得したコード値をプルダウン（`<select>`/`<option>`）として自動的に出力できます。

**根拠**:

1. 基本的な実装（`libraries-tag.json#s30`）

    JSP に以下のように記述すると、コード管理機能の「コード名称テーブル」「コードパターンテーブル」から値を取得してプルダウンが出力されます。

    ```jsp
    <n:codeSelect name="form.gender"
                  codeId="GENDER" pattern="PATTERN2"
                  labelPattern="$VALUE$-$SHORTNAME$"
                  listFormat="div" />
    ```

    出力されるHTML（入力画面）:
    ```html
    <select name="form.gender">
      <option value="MALE">MALE-男</option>
      <option value="FEMALE" selected="selected">FEMALE-女</option>
    </select>
    ```

2. 主な属性（`libraries-tag-reference.json#s51`）

    | 属性 | 説明 |
    |---|---|
    | `name` (必須) | XHTMLのname属性 |
    | `codeId` (必須) | コードID |
    | `pattern` | 使用するパターンのカラム名（表示対象を絞り込む） |
    | `optionColumnName` | 取得するオプション名称のカラム名 |
    | `labelPattern` | ラベル整形パターン。プレースホルダ `$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$` が使用可能（デフォルトは `$NAME$`） |
    | `withNoneOption` | リスト先頭に「選択なし」を追加するか（`true`/`false`、デフォルト `false`） |
    | `noneOptionLabel` | 「選択なし」のラベル |
    | `listFormat` | 確認画面等でのリスト表示フォーマット（`br`/`div`/`span`/`ul`/`ol`/`sp`） |
    | `multiple`, `size`, `disabled`, `onchange` 等 | 通常のHTML select属性 |

3. 表示制御のバリエーション
    - **パターンによる表示項目の切替**（`libraries-code.json#s7`）：コードパターンテーブルのパターン列（例: `PATTERN1`/`PATTERN2`）で機能ごとに表示する値を切替可能。`pattern="PATTERN2"` のように指定。
    - **ソート順**（`libraries-code.json#s9`）：コード名称テーブルの `SORT_ORDER` 列で `<option>` の並び順を制御。
    - **多言語対応**（`libraries-code.json#s8`）：コード名称テーブルに `LANG` 列で言語ごとのデータを用意することで名称の多言語化が可能。
    - **任意ラベル表示**（`libraries-code.json#s10`）：コード名称テーブルに任意カラム（例: `KANA_NAME`）を追加し、`optionColumnName="KANA_NAME"` と `labelPattern="$OPTIONALNAME$"` で表示。

4. プルダウン変更でサブミットする場合（`libraries-tag.json#s16`）

    `onchange` 属性で、サブミットしたいボタンの click を呼び出します（CSP対応時は外部スクリプト/nonce付きscript推奨）。

    ```jsp
    <n:codeSelect name="form.gender"
                  codeId="GENDER"
                  onchange="window.document.getElementById('register').click(); return false;" />
    <n:submit id="register" type="submit" uri="register" value="登録" />
    ```

**注意点**:
- `n:codeSelect` などのカスタムタグは **言語指定によるコード値取得はできません**（ロケール指定なしの `CodeUtil` API を内部で使用）。言語を指定して取得したい場合は、アクションで `CodeUtil.getName(codeId, value, Locale.XXX)` 等を用いて値を取得してください（`libraries-tag.json#s30`, `libraries-code.json#s8`）。
- `pattern` / `optionColumnName` に指定する値は、 `CodePatternSchema.patternColumnNames` 等で設定ファイルに設定したカラム名と **厳密に一致** させる必要があります（`libraries-code.json#s7`）。
- 汎用的な選択肢（コード管理機能を使わないケース）は `n:select` タグを使用しますが、コード値を扱う場合は `n:codeSelect` の利用が基本です（`libraries-tag.json#s9`, `libraries-tag.json#s30`）。

参照:
- `component/libraries/libraries-tag.json#s30` (コード値を表示する)
- `component/libraries/libraries-tag-reference.json#s51` (codeSelectタグ 属性リファレンス)
- `component/libraries/libraries-code.json#s7` (パターンによる表示制御)
- `component/libraries/libraries-code.json#s8` (多言語対応)
- `component/libraries/libraries-code.json#s9` (ソート順)
- `component/libraries/libraries-code.json#s10` (オプション名称)
- `component/libraries/libraries-tag.json#s16` (プルダウン変更でサブミット)
- `component/libraries/libraries-tag.json#s9` (汎用 selectタグ)
