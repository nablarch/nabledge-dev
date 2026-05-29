Step 5-7: 回答を生成し、検証します。

---

**結論**: `SystemTimeProvider` インターフェースの実装クラスをコンポーネント定義で差し替えることで、本番とテストでシステム日時の取得方法を切り替えられる。テスト用には `nablarch.test.FixedSystemTimeProvider` を使うと、任意の固定日時を返させることができる。

**根拠**:

Nablarchの日付管理機能は、コンポーネント定義で指定された `SystemTimeProvider` 実装クラスを通じてシステム日時を取得する仕組みになっている。本番用の設定は以下のとおり：

```xml
<!-- 本番用（BasicSystemTimeProvider = OS日時を返す） -->
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

テスト時は、このコンポーネント定義をテスト用コンポーネント設定ファイルで差し替える。テスティングフレームワークが提供する `FixedSystemTimeProvider` を使えば、任意の固定日時を返させられる：

```xml
<!-- テスト用（FixedSystemTimeProvider = 固定日時を返す） -->
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` プロパティのフォーマット：
| フォーマット | 桁数 |
|---|---|
| yyyyMMddHHmmss | 14桁 |
| yyyyMMddHHmmssSSS | 17桁 |

**切り替えの仕組み**：コンポーネント設定ファイル（XMLファイル）を環境ごとに用意し、本番からの差分として作成する。ユニットテスト実行時は `src/test/resources` のリソースが使用されるため、テスト用のXMLをそこに配置することで自動的に切り替わる：

```
src/
  main/resources/   ← 本番用 systemTimeProvider 設定
  test/resources/   ← テスト用 FixedSystemTimeProvider 設定（差し替え）
```

**注意点**:
- `FixedSystemTimeProvider` は `nablarch.test` パッケージに含まれるテスト専用クラスのため、本番コードには含めない。
- 自前で `SystemTimeProvider` インターフェースを実装したクラスを作成して差し替えることも可能。

参照: `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`, `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s8`, `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s9`, `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s10`

---