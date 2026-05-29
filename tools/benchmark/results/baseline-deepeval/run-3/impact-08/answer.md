Step 5〜8を実行します。

**結論**: テスト時のシステム日時差し替えは、`SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで実現できる。テスト用に `nablarch.test.FixedSystemTimeProvider` が提供されており、コンポーネント設定ファイルを環境ごとに切り替えることで本番とテストを分離できる。

---

## 仕組みの解説

**結論**: テスト時のシステム日時差し替えは、`SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで実現する。テスト用クラス `FixedSystemTimeProvider` が提供されており、本番とテストでコンポーネント設定ファイルを環境別に用意することで切り替えられる。

**根拠**:

Nablarchのシステム日時管理は、コンポーネント定義で指定された `SystemTimeProvider` 実装クラスを通じて行われる。本番環境では `BasicSystemTimeProvider`（OS日時を返す）、テスト環境では固定値を返す `FixedSystemTimeProvider` に差し替えるだけで切り替えできる。

**本番用設定（`src/main/resources` 側）**:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定（`src/test/resources` 側）**:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` に指定できるフォーマット:

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 14桁 |
| `yyyyMMddHHmmssSSS` | 17桁 |

**切り替えの仕組み**:

アーキタイプ生成プロジェクトでは、ユニットテスト実行時（`mvn test`）に `src/test/resources` のリソースが使用される。本番ビルド時（`mvn -P prod package`）は本番環境用のリソースが使用される。コンポーネント設定ファイルを環境ごとのディレクトリに配置することで、ビルド時に自動的に差し替えが行われる。

**注意点**: `SystemTimeProvider` の仕組みを使うには、アプリケーションコードで直接 `new Date()` や `System.currentTimeMillis()` を呼ばず、`SystemTimeUtil` 経由でシステム日時を取得することが前提となる。

参照: `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`, `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`, `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s9`, `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s10`

---