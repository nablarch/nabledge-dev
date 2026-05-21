Step 5〜8: 回答を生成して検証します。

---

**結論**: テスト用コンポーネント設定ファイルで `systemTimeProvider` の実装クラスを `FixedSystemTimeProvider` に差し替えることで、テスト時だけ任意の日時に固定できます。本番では `BasicSystemTimeProvider`（OS日時を返す）を使い、テスト設定ファイルで上書きするだけで切り替えが完了します。

**根拠**:

Nablarchでは `SystemTimeProvider` インターフェースの実装クラスがシステム日時を提供します。コンポーネント定義で指定するクラスを差し替えるだけで取得方法を切り替えられます。

**本番用の設定（OS日時を使用）:**

```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用の設定ファイルで上書き（固定値を使用）:**

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 固定したい日時。フォーマット: `yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁） |

テスト用の設定ファイルでこのコンポーネント定義を上書きしておけば、本番コードは `SystemTimeUtil` を使って日時取得するだけでよく、本番とテストの切り替えはコンポーネント定義のみで完結します。

**注意点**:

- `FixedSystemTimeProvider` はテスティングフレームワーク（`nablarch-testing`）に含まれるため、本番用モジュールには含まれません。テスト用設定ファイルでのみ指定してください。
- このメカニズムはシステム日時（OS日時）の切り替えです。業務日付を切り替えたい場合は `BusinessDateProvider` インターフェースを別途差し替える必要があります。

参照: `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`, `testing-framework-03-Tips.json:s11`, `testing-framework-03-Tips.json:s12`

---