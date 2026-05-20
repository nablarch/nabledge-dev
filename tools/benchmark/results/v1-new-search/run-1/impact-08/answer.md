**結論**: テスト用コンポーネント設定ファイルで `systemTimeProvider` の実装を `nablarch.test.FixedSystemTimeProvider` に差し替えることで、テスト時のみシステム日時を任意の値に固定できる。

**根拠**:

Nablarchのシステム日時はコンポーネント定義で指定された `SystemTimeProvider` 実装クラスから取得される。本番環境では `BasicSystemTimeProvider`、テスト時は `FixedSystemTimeProvider` に差し替える。

**本番用（`src/main/resources` 配下のコンポーネント設定）**:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用（`src/test/resources` 配下のコンポーネント設定）**:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` に指定できる形式:

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 12桁 |
| `yyyyMMddHHmmssSSS` | 15桁 |

切り替えの仕組みとしては、`src/test/resources` 配下に配置したコンポーネント設定が本番設定を上書きするため、テスト実行時は自動的に `FixedSystemTimeProvider` が使用される。本番ビルド時（`mvn -P prod package`）は `src/test/resources` が含まれないため、本番設定がそのまま使用される。

**注意点**: より柔軟に任意の実装に切り替えたい場合（例：テストメソッドごとに日時を変えたい）は、`SystemTimeProvider` インタフェースを自前で実装したクラスを作成し、同様に差し替えることもできる。

参照: `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`, `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`