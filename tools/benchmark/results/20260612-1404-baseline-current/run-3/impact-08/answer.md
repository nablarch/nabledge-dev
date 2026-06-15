**結論**: テスト用クラス `FixedSystemTimeProvider` を `systemTimeProvider` コンポーネントとしてテスト用設定ファイルに登録することで、テスト時のみシステム日時を任意の固定値に差し替えられる。本番とテストの切り替えは、コンポーネント設定ファイル（XML）を環境ごとに差し替えることで実現する。

**根拠**:

**仕組み**

Nablarchでは `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供する。コンポーネント定義で指定するクラスを差し替えるだけで、アプリケーション全体のシステム日時の取得方法を切り替えられる。

| 環境 | 使用クラス |
|------|-----------|
| 本番 | `nablarch.core.date.BasicSystemTimeProvider` |
| テスト | `nablarch.test.FixedSystemTimeProvider` |

**本番用設定**（`src/main/resources` 側のコンポーネント設定ファイル）:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（`src/test/resources` 側のコンポーネント設定ファイル）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` プロパティに指定できるフォーマット:

| フォーマット | 説明 |
|-------------|------|
| `yyyyMMddHHmmss`（12桁） | 例: `20100913123456` |
| `yyyyMMddHHmmssSSS`（15桁） | ミリ秒まで指定する場合 |

**環境ごとの切り替え方法**

コンポーネント設定ファイル（XMLファイル）を切り替えることで、環境ごとにコンポーネントを差し替えられる。まず本番用コンポーネント定義を作成し、その後、環境ごとの差分として別の定義ファイルを作成して環境ごとのディレクトリに配置する。ユニットテスト実行時は `src/test/resources` が使用されるため、テスト用の設定ファイルをここに配置することで自動的に差し替えが有効になる。

**注意点**:
- `FixedSystemTimeProvider` は `nablarch.test` パッケージに属するテスト用クラスであり、本番環境には含めないこと。
- 登録日時や更新日時など日付に依存するテスト項目は、このクラスで固定値を設定しないと「日によって想定結果が変わる」ため自動テストで正しさを確認できない。

参照: `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`, `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`, `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s9`, `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s10`