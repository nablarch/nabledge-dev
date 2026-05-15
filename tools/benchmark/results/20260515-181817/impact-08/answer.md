**結論**: テスト時にシステム日時を固定値に差し替えるには、`FixedSystemTimeProvider`（テスト用クラス）をコンポーネント定義で指定します。本番とテストの切り替えは、環境別のコンポーネント設定ファイルで `systemTimeProvider` の実装クラスを差し替えることで実現できます。

**根拠**:

Nablarch の日付管理機能は、`SystemTimeProvider` インタフェースの実装クラス経由でシステム日時を提供します。コンポーネント定義でこの実装クラスを差し替えるだけで切り替えが可能です。

**本番環境**（通常の OS 日時を使用）:
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト環境**（任意の日時に固定）:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` プロパティには以下のフォーマットで日時を指定します:
- `yyyyMMddHHmmss`（14桁）
- `yyyyMMddHHmmssSSS`（17桁）

テスト内でシステム日時を取得する場合は以下のようにします:
```java
SystemTimeProvider provider =
    (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

アプリケーション側は `SystemTimeUtil` を使用してシステム日時を取得するため、コンポーネント定義だけ切り替えればアプリコードの変更は不要です。

**注意点**:
- `FixedSystemTimeProvider` は `nablarch-testing` モジュールに含まれるテスト用クラスのため、本番用の依存関係には含めないこと（`test` スコープで依存定義するのが望ましい）
- `systemTimeProvider` というコンポーネント名で登録することが必須
- 業務日付（`BusinessDateProvider`）とシステム日時（`SystemTimeProvider`）は別々に管理されているため、業務日付の差し替えが必要な場合は `BusinessDateProvider` の実装クラスも別途差し替えが必要

参照: `component/libraries/libraries-date.json#s2`, `component/libraries/libraries-date.json#s5`, `component/libraries/libraries-date.json#s12`, `development-tools/testing-framework/testing-framework-03-Tips.json#s11`, `development-tools/testing-framework/testing-framework-03-Tips.json#s12`