Step 5-8: 回答を生成します。

**read_sections** に渡したファイル:
- `component/libraries/libraries-date.json:s2`
- `component/libraries/libraries-date.json:s5`
- `component/libraries/libraries-date.json:s12`
- `development-tools/testing-framework/testing-framework-03-Tips.json:s11`
- `development-tools/testing-framework/testing-framework-03-Tips.json:s12`
- `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s9`
- `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s10`

---

**結論**: `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで、本番とテストのシステム日時を切り替えられる。テスト時は `FixedSystemTimeProvider` を使うと任意の日時に固定できる。

**根拠**:

本番用の設定（`src/main/resources` 等）では `BasicSystemTimeProvider` を使用する。

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

テスト用の設定（`src/test/resources` 等）では `FixedSystemTimeProvider` を指定し、固定したい日時を `fixedDate` プロパティに設定する。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| `fixedDate` | 固定したい日時を文字列で指定。フォーマットは `yyyyMMddHHmmss`（14桁）または `yyyyMMddHHmmssSSS`（17桁）|

**切り替えの仕組み**:
- Nablarchは `systemTimeProvider` という名前のコンポーネントからシステム日時を取得する
- テスト環境のコンポーネント設定ファイルで上記テスト用クラスに差し替えるだけでよく、アプリケーションコードの変更は不要
- Mavenプロファイルを使って環境ごとにコンポーネント設定ファイルを切り替えることで、本番とテストを自動的に使い分けられる

**注意点**: `FixedSystemTimeProvider` は `nablarch-testing` モジュールに含まれるクラスのため、テスト用の依存関係として追加すること。

参照: `libraries-date.json:s2`, `libraries-date.json:s5`, `libraries-date.json:s12`, `testing-framework-03-Tips.json:s11`, `testing-framework-03-Tips.json:s12`

---