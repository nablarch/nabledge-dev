**結論**: テスト時のみシステム日時を任意の日付に固定するには、テスト用コンポーネント設定ファイルで `systemTimeProvider` を `nablarch.test.FixedSystemTimeProvider` に差し替えます。

**根拠**:

Nablarch では `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供します。コンポーネント定義で指定するクラスを差し替えるだけで、本番とテストを切り替えられます。

**本番用コンポーネント設定:**
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用コンポーネント設定（固定日時）:**
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| プロパティ名 | 設定内容 |
|---|---|
| `fixedDate` | 固定したい日時を文字列で指定。`yyyyMMddHHmmss`（14桁）または `yyyyMMddHHmmssSSS`（17桁） |

テスト用設定ファイルを本番設定ファイルとは別に用意し、テスト実行時にテスト用設定を読み込ませることで切り替えが実現できます。

**業務日付を切り替えたい場合:**

業務日付は `BusinessDateProvider` インタフェースを実装したクラスを差し替えます。また、特定区分の業務日付だけを上書きしたい場合はシステムプロパティで指定できます:
```
-DBasicBusinessDateProvider.<区分>=yyyyMMdd
# 例: -DBasicBusinessDateProvider.batch=20160317
```

**注意点**:
- `FixedSystemTimeProvider` はテスティングフレームワークが提供するクラスのため、本番コードでは使用しないこと
- コンポーネント名は必ず `systemTimeProvider` とすること（フレームワークがこの名前で参照する）
- 独自のロジックが必要な場合（テストケースごとに日時を変えるなど）は `SystemTimeProvider` を独自実装して差し替えることも可能

参照: `component/libraries/libraries-date.json#s2`, `component/libraries/libraries-date.json#s5`, `component/libraries/libraries-date.json#s12`, `development-tools/testing-framework/testing-framework-03-Tips.json#s11`, `development-tools/testing-framework/testing-framework-03-Tips.json#s12`