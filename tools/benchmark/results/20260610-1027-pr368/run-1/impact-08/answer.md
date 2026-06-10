**結論**: テスト時にシステム日時を任意の値に固定するには、コンポーネント設定ファイルで `systemTimeProvider` コンポーネントを `nablarch.test.FixedSystemTimeProvider` に差し替える。本番では `BasicSystemTimeProvider` を使い、テスト用設定ファイルで上書きする形で切り替えできる。

**根拠**:

Nablarchでは、`SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供する仕組みになっている。コンポーネント定義で指定するクラスを差し替えるだけで、システム日時の取得方法を切り替えられる。

**本番用コンポーネント設定**:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用コンポーネント設定**（本番設定を上書き）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` プロパティには以下のいずれかのフォーマットで日時を指定する:
- `yyyyMMddHHmmss`（12桁）
- `yyyyMMddHHmmssSSS`（15桁）

設定後、通常通り `SystemTimeProvider` からシステム日時を取得できる:
```java
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**仕組みのポイント**: テスト用設定ファイル（例: `unit-test.xml`）で同名コンポーネント `systemTimeProvider` を `FixedSystemTimeProvider` で上書きすれば、テスト実行時だけ固定値が返る。本番の設定ファイルは変更不要。

**注意点**:
- `FixedSystemTimeProvider` はテストフレームワーク（`nablarch-testing` モジュール）に含まれるため、本番コードのクラスパスには含めないこと。
- テスト用設定ファイルを使う場合は、本番設定ファイルとテスト設定ファイルで `systemTimeProvider` の定義が分離されていることを確認すること。

参照: testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12