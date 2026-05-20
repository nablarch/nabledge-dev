**結論**: テスト時のシステム日時固定は、テスト用コンポーネント設定ファイルで `systemTimeProvider` コンポーネントを `FixedSystemTimeProvider` に差し替えることで実現できる。

**根拠**:

Nablarchのシステム日時は `SystemTimeProvider` インタフェースを実装したクラスがコンポーネント定義で提供する仕組みになっている。差し替えるだけで切り替えができる。

**本番用設定**:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定**（テスト用コンポーネント設定ファイルで上書き）:
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

テスト内でシステム日時を取得する場合:
```java
SystemTimeProvider provider =
    (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**注意点**: テスト用コンポーネント設定ファイルで本番の `systemTimeProvider` 定義を上書きする形で適用する。本番コードを変更する必要はない。

参照: component/libraries/libraries-date.json:s5, s12 / development-tools/testing-framework/testing-framework-03-Tips.json:s11, s12