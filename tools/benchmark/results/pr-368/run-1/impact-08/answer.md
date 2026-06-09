**結論**: テスト時のシステム日時差し替えは、`SystemTimeProvider`インタフェースの実装クラスをコンポーネント定義で差し替えることで実現できる。Nablarchはテスト用に`nablarch.test.FixedSystemTimeProvider`を提供しており、このクラスをコンポーネント名`systemTimeProvider`に設定することで任意の日時を固定返却させることができる。

**根拠**:

Nablarchの日付管理機能は、コンポーネント定義で指定するクラスによってシステム日時の取得方法を決定する設計になっている。本番環境では以下のように`BasicSystemTimeProvider`（OSのシステム日時を返す実装）を設定する。

```xml
<!-- 本番用設定 -->
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

テスト時には、同じコンポーネント名`systemTimeProvider`に`FixedSystemTimeProvider`を指定し、`fixedDate`プロパティで固定する日時を設定する。

```xml
<!-- テスト用設定（コンポーネント設定ファイルで差し替え） -->
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 指定したい日時を以下のフォーマットいずれかに合致する文字列で指定する。<br>・yyyyMMddHHmmss (12桁)<br>・yyyyMMddHHmmssSSS (15桁) |

この差し替えにより、テスト実行時に`SystemTimeUtil`経由で取得するシステム日時が固定値になるため、登録日時・更新日時など日付に依存するテストの期待値を安定させることができる。

**業務日付の切り替えも同様の仕組みで対応できる。** `BusinessDateProvider`インタフェースを実装したクラスを作成し、コンポーネント名`businessDateProvider`に設定することで切り替えられる。

**注意点**:
- 切り替えはコンポーネント定義ファイルの差し替えで行うため、テスト用コンポーネント設定ファイルを本番とは別に用意するか、テスト時にのみ読み込まれる設定ファイルで上書きする運用が一般的になる。
- 業務日付の上書きは、コンポーネント差し替えに加えて、バッチ再実行時に限りシステムプロパティ（`-DBasicBusinessDateProvider.<区分>=yyyyMMdd`形式）で一時的に上書く方法もある。

参照: `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`, `component/libraries/libraries-date.json:s13`, `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`