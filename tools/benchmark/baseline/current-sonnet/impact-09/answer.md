**結論**: Nablarch のコード管理機能（`nablarch-common-code`）とバリデーションアノテーション `@CodeValue` を組み合わせることで、マスタ上で定義された有効なコード値かどうかを入力チェックと連携できる。

**根拠**:

1. **コード管理機能の仕組み** (`component/libraries/libraries-code.json:s1`)
   - コードパターンテーブルとコード名称テーブルの2テーブルでコード情報を管理する。
   - テーブルの `VALUE` 列に `male` / `female` などのコード値を、`NAME` 列に「男性」「女性」などの名称を登録する。
   - アプリ起動時に `BasicCodeLoader` → `BasicStaticDataCache` → `BasicCodeManager` の構成でDBからキャッシュに読み込む（`codeManager` というコンポーネント名で登録必須）。

2. **@CodeValue アノテーションによる入力チェック** (`component/libraries/libraries-code.json:s6`)
   - Bean Validation 用: `nablarch.common.code.validator.ee.CodeValue`
   - Nablarch Validation 用: `nablarch.common.code.validator.CodeValue`
   - フォームのフィールドに `@CodeValue(codeId = "GENDER")` を付けるだけで、コード管理テーブルに存在する有効な値かをバリデーション時に自動チェックする。
   ```java
   // Bean Validation の例
   @CodeValue(codeId = "GENDER")
   private String gender;
   ```

3. **パターンを使った有効値の絞り込み** (`component/libraries/libraries-code.json:s6`, `component/libraries/libraries-code.json:s2`)
   - コードパターンテーブルの `PATTERN` 列（0/1 フラグ）を使うと、機能ごとに有効な値のサブセットを切り替えられる。
   - バリデーション時も同パターン内の有効値かチェックするには `pattern` 属性を指定する:
   ```java
   @CodeValue(codeId = "GENDER", pattern = "PATTERN2")
   private String gender;
   ```
   - 画面（JSP）側でも同じパターンを指定してプルダウンを絞り込める:
   ```jsp
   <n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
   ```

**注意点**:
- コード管理機能は「静的なコード情報（値と名称のマッピング）」を対象としており、商品コード・企業コードのように値が動的に変化するマスタは対象外。動的なマスタはアプリケーション側でマスタテーブルを作成して対応すること (`component/libraries/libraries-code.json:s1`)。
- RDBMS の参照整合性制約はコード管理機能と併用できない。制約チェックには `@CodeValue` を使用すること (`component/libraries/libraries-code.json:s1`)。
- ドメインバリデーションと組み合わせる場合、1 つのドメインには 1 つのパターンしか指定できない。複数パターンに対応するにはパターンごとにドメインを定義する (`component/libraries/libraries-code.json:s6`)。

参照: component/libraries/libraries-code.json:s1, component/libraries/libraries-code.json:s2, component/libraries/libraries-code.json:s6