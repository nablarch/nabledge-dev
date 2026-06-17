**結論**: Nablarchでは `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで、本番とテストのシステム日時を切り替えられます。テスト用には `nablarch.test.FixedSystemTimeProvider` を使い、任意の固定日時を設定します。

**根拠**:

**仕組み**

アプリケーションは `systemTimeProvider` という名前のコンポーネントを通じてシステム日時を取得します。コンポーネント定義で指定するクラスを差し替えるだけで、日時の取得方法を切り替えられます。

**本番用設定** (`src/main/resources/` などの本番用設定ファイル):

```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定** (`src/test/resources/` などのテスト用設定ファイル):

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| `fixedDate` | 固定したい日時を `yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁）形式で指定 |

**アプリケーションコードでのシステム日時取得** (変更不要):

```java
// SystemTimeUtil を通じて取得。本番/テストどちらの設定でも同じ呼び出しで動作する
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**切り替えの実現方法**

Maven プロファイルを使い、環境別ディレクトリ (`src/env/dev/`, `src/env/prod/` など) にそれぞれのコンポーネント設定ファイルを配置します。ユニットテスト実行時は `src/test/resources/` 配下の設定ファイルが使われるため、そちらに `FixedSystemTimeProvider` を定義します。

**注意点**:
- `FixedSystemTimeProvider` は `nablarch-testing` モジュールに含まれます。テストスコープ（`<scope>test</scope>`）で依存関係に追加する必要があります。
- 独自の切り替えロジックが必要な場合は、`SystemTimeProvider` インタフェースを独自実装して設定することもできます。

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s12, testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12