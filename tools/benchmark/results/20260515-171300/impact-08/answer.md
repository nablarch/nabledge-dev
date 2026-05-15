**結論**: テスト時のシステム日時差し替えは、`FixedSystemTimeProvider` をコンポーネント定義で差し替えるだけで実現できます。

**根拠**:

Nablarch では `SystemTimeProvider` インターフェースの実装クラスがシステム日時を提供します。コンポーネント定義で指定するクラスを切り替えるだけで、本番とテストを切り替えられます。

**本番用設定**（OS 日時を使用）:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（固定値を返す）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` プロパティに指定できるフォーマット:

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 14桁 |
| `yyyyMMddHHmmssSSS` | 17桁 |

切り替え方法は、テスト用コンポーネント定義ファイルに上記の設定を記述するだけです。コンポーネント名 `systemTimeProvider` は本番・テストで共通のため、定義ファイルを差し替えるだけでコード変更は不要です。

カスタムの切り替えロジック（シナリオごとに異なる日時を返す等）が必要な場合は、`SystemTimeProvider` インターフェースを独自実装したクラスを作成してコンポーネントに登録します。

**注意点**:
- `FixedSystemTimeProvider` は `nablarch-test` モジュールに含まれており、テストスコープの依存にとどめること
- 業務日付（`BusinessDateProvider`）も同様のパターンで切り替え可能（実装クラスを差し替えてコンポーネント名 `businessDateProvider` で登録）
- コンポーネント名は必ず `systemTimeProvider` を使用すること

参照: `component/libraries/libraries-date.json#s2`, `component/libraries/libraries-date.json#s5`, `component/libraries/libraries-date.json#s12`, `development-tools/testing-framework/testing-framework-03-Tips.json#s11`, `development-tools/testing-framework/testing-framework-03-Tips.json#s12`