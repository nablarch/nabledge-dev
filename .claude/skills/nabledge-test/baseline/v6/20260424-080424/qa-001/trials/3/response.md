**結論**: コード値のプルダウン入力は、Nablarchの **codeSelectタグ** (`<n:codeSelect>`) を使用して実装します。コード管理機能 (コード管理テーブル + codeManager コンポーネント) の初期設定を行い、JSPでcodeSelectタグに`codeId`を指定することで、コード管理テーブルに登録されたコード値を自動的にプルダウン(select/option)として出力できます。

**根拠**:

1. **JSPでの実装**: `codeSelectタグ` を使用してコードIDを指定する。

   ```jsp
   <n:codeSelect name="form.gender" codeId="GENDER" pattern="PATTERN2" cssClass="form-control" />
   ```

   主な属性 (libraries-tag-reference.json#s51):
   - `name` (必須): XHTMLのname属性
   - `codeId` (必須): コードID
   - `pattern`: 使用するパターンのカラム名
   - `labelPattern`: ラベル整形パターン (`$NAME$` / `$SHORTNAME$` / `$OPTIONALNAME$` / `$VALUE$`)
   - `withNoneOption` / `noneOptionLabel`: 先頭に「選択なし」オプションを追加
   - `multiple`, `size`, `disabled`, `onchange` などの標準属性

2. **コード管理の初期設定** (libraries-code.json#s6): `コードパターンテーブル` と `コード名称テーブル` の2テーブルを作成し、以下のコンポーネントをXMLで設定する。
   ```xml
   <component name="codeLoader" class="nablarch.common.code.BasicCodeLoader">
     <property name="codePatternSchema">...</property>
     <property name="codeNameSchema">...</property>
   </component>
   <component name="codeCache" class="nablarch.core.cache.BasicStaticDataCache">
     <property name="loader" ref="codeLoader"/>
     <property name="loadOnStartup" value="false"/>
   </component>
   <component name="codeManager" class="nablarch.common.code.BasicCodeManager">
     <property name="codeDefinitionCache" ref="codeCache"/>
   </component>
   ```

3. **入力値チェック** (libraries-code.json#s11): 受信したコード値の妥当性は `@CodeValue` アノテーションでチェックする。
   ```java
   @CodeValue(codeId = "GENDER")
   private String gender;
   ```
   パターン使用時は `@CodeValue(codeId = "GENDER", pattern = "PATTERN2")` と指定。

4. **任意リストをプルダウンで出す場合** (libraries-tag.json#s9): コード管理を使わず任意リストを出す場合は `n:select` を使い、アクションでリクエストスコープに選択肢リストを設定する。
   ```jsp
   <n:select name="form.plan1" listName="plans"
             elementLabelProperty="planName" elementValueProperty="planId" />
   ```

**注意点**:
- `BasicCodeManager` のコンポーネント名は必ず **codeManager** にすること (libraries-code.json#s6)。
- `BasicCodeLoader` と `BasicStaticDataCache` は初期化が必要なため、`BasicApplicationInitializer` の initializeList に含めること。
- 機能ごとに表示/非表示を切り替えたい場合はコードパターンテーブルのパターン列を使い、JSPでは `pattern` 属性、バリデーションでは `@CodeValue(..., pattern = "...")` の両方で同じパターン名を指定すること (libraries-code.json#s7, s11)。
- `pattern` 属性の値は設定ファイルで定義したカラム名と厳密に一致させる必要がある。

参照:
- `component/libraries/libraries-tag-reference.json#s51` (codeSelectタグ)
- `component/libraries/libraries-tag.json#s9` (選択項目の表示)
- `component/libraries/libraries-code.json#s6` (初期設定)
- `component/libraries/libraries-code.json#s7` (パターンによる切替)
- `component/libraries/libraries-code.json#s11` (入力値チェック)
