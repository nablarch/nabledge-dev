**結論**: テスト時のシステム日時固定は、コンポーネント定義で `SystemTimeProvider` の実装クラスを `FixedSystemTimeProvider`（テスト用）に差し替えることで実現できます。

**根拠**:

Nablarch では、システム日時の提供を `SystemTimeProvider` インタフェースの実装クラスに委譲しています。コンポーネント定義でこのクラスを差し替えるだけで切り替えが可能です。

**本番用設定**（通常のOS日時を返す）:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（任意の固定日時を返す）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` プロパティには以下いずれかのフォーマットで指定します：

| フォーマット | 例 |
|---|---|
| `yyyyMMddHHmmss`（14桁） | `20100914123456` |
| `yyyyMMddHHmmssSSS`（17桁） | `20100914123456000` |

システム日時の取得はアプリケーションコードで `SystemTimeUtil` を使用します。テストコードから直接取得する場合は以下の通りです：
```java
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**注意点**:
- `FixedSystemTimeProvider` はテスト用モジュール（`nablarch.test`）に含まれるため、本番コードに混入しないよう依存スコープを `test` に限定してください。
- テスト用・本番用の設定ファイルを分けて管理し、テスト実行時のみテスト用コンポーネント定義が読み込まれるよう構成してください。
- この仕組みは業務日付（`BusinessDate`）にも同様に適用できます（`libraries-date.json#s13`参照）。

参照: `development-tools/testing-framework/testing-framework-03-Tips.json#s11`, `development-tools/testing-framework/testing-framework-03-Tips.json#s12`, `component/libraries/libraries-date.json#s2`, `component/libraries/libraries-date.json#s12`