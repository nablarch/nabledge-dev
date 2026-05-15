**結論**: テスト時にシステム日時を任意の日付に固定するには、コンポーネント定義で `SystemTimeProvider` の実装クラスを `FixedSystemTimeProvider`（テスト用）に差し替えます。本番とテストでコンポーネント定義ファイルを切り替えることで対応できます。

**根拠**:

Nablarch のシステム日時管理機能は、`SystemTimeProvider` インターフェースの実装クラスをコンポーネント定義で指定する仕組みになっています。クラスを差し替えるだけで動作を切り替えられます。

**本番環境（通常）の設定**:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト環境（固定日時）の設定**:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` プロパティに指定できるフォーマット:

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 14桁 |
| `yyyyMMddHHmmssSSS` | 17桁 |

テストコードからは以下のように取得できます:
```java
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**注意点**:
- `FixedSystemTimeProvider` は `nablarch.test` パッケージ（テストフレームワーク）に含まれるため、本番コードのクラスパスには含めないよう注意してください。
- 業務日付（`BusinessDateProvider`）を切り替えたい場合も同様の手順で対応可能です。テスト用の `BusinessDateProvider` 実装クラスを作成し、コンポーネント定義で差し替えます。
- 切り替えはコンポーネント定義ファイルの差し替えで行うため、アプリケーションコードの変更は不要です。

参照: `development-tools/testing-framework/testing-framework-03-Tips.json#s11`, `development-tools/testing-framework/testing-framework-03-Tips.json#s12`, `component/libraries/libraries-date.json#s2`, `component/libraries/libraries-date.json#s12`