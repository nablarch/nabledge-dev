**結論**: NablarchのDI設計により、`SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えるだけで本番・テストの切り替えが可能。テスト用の固定日時返却クラス `FixedSystemTimeProvider` が標準提供されている。

---

**根拠**:

Nablarchではシステム日時の取得が `SystemTimeProvider` インタフェースを通じてDIコンテナ経由で行われる。この実装クラスをコンポーネント定義で指定する構造になっているため、クラスを差し替えるだけで動作を切り替えられる。

**本番用設定**（`BasicSystemTimeProvider` — OS時刻をそのまま返す）:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（`FixedSystemTimeProvider` — 任意の固定日時を返す）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` プロパティに指定できるフォーマット:
- `yyyyMMddHHmmss`（14桁）
- `yyyyMMddHHmmssSSS`（17桁）

**本番・テスト切り替えの仕組み**:
- ユニットテスト実行時（`mvn test`）は `src/test/resources` のコンポーネント設定ファイルが使用される（devプロファイルがデフォルト）
- 本番ビルド時（`mvn -P prod package`）は `src/env/prod/` のリソースが使用される
- つまり、テスト用コンポーネント設定ファイルを `src/test/resources` に配置することで、テスト時のみ `FixedSystemTimeProvider` が有効になる

**カスタム実装が必要な場合**: 固定値以外の切り替えロジック（例：テスト中に時刻を進める等）が必要なら、`SystemTimeProvider` インタフェースを実装したクラスを作成してコンポーネント定義に設定すればよい。

**注意点**: 業務日付（`BusinessDateProvider` インタフェース）も同じ仕組みで切り替えが可能。業務日付は通常DBで管理されるが、テスト時は `BusinessDateProvider` の実装クラスを差し替えることで任意の値を返せる。

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12, libraries-date.json:s13, testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, setting-guide-ManagingEnvironmentalConfiguration.json:s8, setting-guide-ManagingEnvironmentalConfiguration.json:s9

---