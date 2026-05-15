**結論**: テスト時にシステム日時を固定値に差し替えるには、`nablarch.test.FixedSystemTimeProvider` を使用する。本番とテストでコンポーネント定義ファイルを切り替えることで対応できる。

**根拠**:

Nablarch では `SystemTimeProvider` インターフェースの実装クラスがシステム日時を提供する設計になっており、このクラスをコンポーネント定義で差し替えるだけで動作を切り替えられる。

**本番用設定**（通常はOS日時を返す `BasicSystemTimeProvider`）:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（`FixedSystemTimeProvider` で任意の日時に固定）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20260331235959" />
</component>
```

`fixedDate` プロパティに指定できるフォーマット:

| フォーマット | 桁数 | 例 |
|---|---|---|
| `yyyyMMddHHmmss` | 14桁 | `20260331235959` |
| `yyyyMMddHHmmssSSS` | 17桁 | `20260331235959000` |

**切り替え方法**:
- テスト用コンポーネント定義ファイル（例: `unit-test.xml`）に `FixedSystemTimeProvider` を設定し、テスト実行時にそのファイルを読み込むよう構成する
- 本番用ファイルには `BasicSystemTimeProvider` を設定する
- コンポーネント名は必ず `systemTimeProvider` とする

締め処理のテストの場合、締め日の日付を `fixedDate` に指定することで、その日付でシステムが動作しているかのようにテストできる。

**注意点**:
- `FixedSystemTimeProvider` はテストライブラリ（`nablarch-testing`）に含まれるクラスであり、本番コードには使用しない
- 業務日付（`BusinessDateProvider`）はシステム日時とは別管理。締め処理が業務日付を参照している場合は `BusinessDateProvider` の実装クラスも別途差し替えが必要
- コンポーネント名 `systemTimeProvider` は固定。この名前でなければ機能しない

参照: `development-tools/testing-framework/testing-framework-03-Tips.json#s11`, `development-tools/testing-framework/testing-framework-03-Tips.json#s12`, `component/libraries/libraries-date.json#s2`, `component/libraries/libraries-date.json#s5`