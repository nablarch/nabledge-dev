**結論**: コンポーネント定義で `systemTimeProvider` という名前のコンポーネントを差し替えることで、本番とテストのシステム日時を切り替えられます。テスト用には `nablarch.test.FixedSystemTimeProvider` を使うと任意の固定日時を返すことができます。

**根拠**:

Nablarchのシステム日時管理機能は `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供する仕組みです。コンポーネント定義で指定するクラスを差し替えるだけで切り替えられるため、アプリケーションコードの変更は不要です。

**本番用設定**:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（テスト用コンポーネント設定ファイルで上書き）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` には以下のいずれかのフォーマットで固定したい日時を指定します:
- `yyyyMMddHHmmss`（14桁）
- `yyyyMMddHHmmssSSS`（17桁）

テスト実行中は `FixedSystemTimeProvider` が `systemTimeProvider` として動作するため、`SystemTimeUtil` 経由で取得するシステム日時が常に指定した固定値になります。

**注意点**: `FixedSystemTimeProvider` 以外にも、`SystemTimeProvider` インタフェースを実装したカスタムクラスを作成してコンポーネント定義に設定することで、任意のロジック（オフセット加算など）でシステム日時を切り替えることも可能です。

参照: `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`, `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`