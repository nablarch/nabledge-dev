**結論**: テスト時にシステム日時を固定するには、コンポーネント定義の `systemTimeProvider` を `FixedSystemTimeProvider` に差し替える。本番では `BasicSystemTimeProvider` を使い、テスト用設定ファイルで上書きするだけで切り替えられる。

**根拠**:

Nablarch では `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供する。テスト用設定ファイルで以下のように `FixedSystemTimeProvider` を指定することで、任意の日時に固定できる。

**テスト用コンポーネント定義**（例: 2010年9月13日12時34分56秒に固定）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

**本番用コンポーネント定義**:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

`fixedDate` に指定できるフォーマット:
- `yyyyMMddHHmmss`（14桁）
- `yyyyMMddHHmmssSSS`（17桁）

コンポーネント定義で指定するクラスを差し替えるだけでよいため、本番とテストの切り替えは設定ファイルの分離で実現できる。

**注意点**: 締め処理が「業務日付」（データベース管理の業務上の日付）を参照している場合は、`BasicBusinessDateProvider` の設定ファイルを差し替えるか、テストデータのデータベース値を直接変更する必要がある。業務日付をテスト用に切り替えるには `BusinessDateProvider` インタフェースを実装したクラスを作成してコンポーネント定義に設定する。

参照: `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`, `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`