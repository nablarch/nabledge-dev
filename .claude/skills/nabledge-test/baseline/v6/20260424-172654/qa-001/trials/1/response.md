**結論**: Nablarchでコード値のプルダウン入力を実装するには、カスタムタグ `<n:codeSelect>` を使用します。コード管理機能のコードIDを `codeId` 属性で指定することで、コードパターンテーブル/コード名称テーブルに登録されたコード値をプルダウン (`<select>`) として自動的に出力できます。

**根拠**:

1. カスタムタグの選択
   コード値専用のカスタムタグとして、次のタグが提供されている (libraries-tag.json#s30)。
   - `codeタグ` (コード値表示)
   - `codeSelectタグ` (コード値のプルダウン)
   - `codeCheckboxタグ` / `codeRadioButtonsタグ` / `codeCheckboxesタグ`

2. 基本的な実装例 (libraries-tag.json#s30)
   前提として、コードパターンテーブルとコード名称テーブルにコードを登録する。例えば `GENDER` コードに MALE/FEMALE/OTHER を登録しておく。

   JSP:
   ```jsp
   <n:codeSelect name="form.gender"
                 codeId="GENDER" pattern="PATTERN2"
                 labelPattern="$VALUE$-$SHORTNAME$"
                 listFormat="div" />
   ```

   出力されるHTML:
   ```html
   <!-- 入力画面 -->
   <select name="form.gender">
     <option value="MALE">MALE-男</option>
     <option value="FEMALE" selected="selected">FEMALE-女</option>
   </select>
   ```

3. 主な属性 (libraries-tag-reference.json#s51)
   - `name` (必須): 入力項目のname属性
   - `codeId` (必須): コードID
   - `pattern`: 使用するパターン列のカラム名 (表示/非表示切替に利用)
   - `optionColumnName`: オプション名称のカラム名
   - `labelPattern`: ラベル整形パターン。プレースホルダは `$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$`。デフォルトは `$NAME$`
   - `listFormat`: リスト表示フォーマット (`br`/`div`/`span`/`ul`/`ol`/`sp`)
   - `withNoneOption` / `noneOptionLabel`: 「選択なし」項目を先頭に追加する場合に使用

4. パターンによる表示制御 (libraries-code.json#s7)
   機能ごとに表示するコードを切り替えたい場合は、コードパターンテーブルに `PATTERN1` `PATTERN2` といったパターンカラムを定義し、`pattern` 属性に指定する。
   ```jsp
   <n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
   ```

5. オプション名称の表示 (libraries-code.json#s10)
   標準の名称/略称以外の表示名称を使用したい場合は、コード名称テーブルにオプション名称カラム (例: `KANA_NAME`) を追加し、`optionColumnName` と `labelPattern` に `$OPTIONALNAME$` を指定する。
   ```jsp
   <n:codeSelect name="form.gender" codeId="GENDER"
                 optionColumnName="KANA_NAME"
                 labelPattern="$OPTIONALNAME$" />
   ```

6. プルダウン変更でサブミットしたい場合 (libraries-tag.json#s16)
   `onchange` 属性でサブミット対象ボタンの click を呼び出す。
   ```jsp
   <n:codeSelect name="form.plan" codeId="PLAN"
                 onchange="window.document.getElementById('register').click(); return false;" />
   <n:submit id="register" type="submit" uri="register" value="登録" />
   ```

**注意点**:
- カスタムタグ (`n:codeSelect` 等) では、言語指定によるコード値の取得はできない (ロケールを指定しないAPIを使用しているため)。言語指定が必要な場合はアクション側で `CodeUtil` を使用してコード値を取得する (libraries-tag.json#s30)。
- `pattern` 属性で指定するカラム名は、`CodePatternSchema.patternColumnNames` に設定したカラム名と厳密に一致させる必要がある (libraries-code.json#s7)。
- `$OPTIONALNAME$` プレースホルダを使う場合、`optionColumnName` の指定が必須となる (libraries-tag-reference.json#s51)。
- コード値ではなく任意のオブジェクトのリストをプルダウン表示したい場合は、汎用の `<n:select>` タグをリクエストスコープの選択肢リストと組み合わせて使用する (libraries-tag.json#s9)。

参照:
- component/libraries/libraries-tag.json#s30 (codeSelect 実装例)
- component/libraries/libraries-tag-reference.json#s51 (codeSelect 属性一覧)
- component/libraries/libraries-code.json#s7 (パターンによる表示切替)
- component/libraries/libraries-code.json#s10 (オプション名称の表示)
- component/libraries/libraries-tag.json#s16 (プルダウン変更でサブミット)
- component/libraries/libraries-tag.json#s9 (汎用 select タグ)
