**結論**: Nablarchでは、コンポーネント定義で `SystemTimeProvider` の実装クラスを差し替えることで、テスト時のみシステム日時を任意の値に固定できる。テスト環境用の設定ファイルで `FixedSystemTimeProvider` を指定し、本番環境では `BasicSystemTimeProvider` を使う構成にすることで本番/テストの切り替えが実現できる。

**根拠**:

Nablarchの日付管理機能では、`systemTimeProvider` というコンポーネント名で登録されたクラスがシステム日時を提供する。このクラスを差し替えるだけで動作を切り替えられる仕組みになっている。

**本番用設定（BasicSystemTimeProvider）:**

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定（FixedSystemTimeProvider）:**

コンポーネント設定ファイルで `SystemTimeProvider` インタフェースの実装クラスを指定する箇所に `FixedSystemTimeProvider` を指定し、固定したい日時を設定する。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 指定したい日時を以下のフォーマットいずれかに合致する文字列で指定する。 `yyyyMMddHHmmss`（14桁）または `yyyyMMddHHmmssSSS`（17桁） |

テスト用設定ファイル内でこのコンポーネントを上書きすることで、テスト実行時のみシステム日時を固定できる。

取得方法はどちらの環境でも同じ `SystemTimeUtil` を使えばよい:

```java
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**注意点**:
- `FixedSystemTimeProvider` はテスティングフレームワーク（`nablarch-testing`モジュール）が提供するクラスで、本番環境には含めないこと。
- テスト用コンポーネント定義ファイル（例: `unit-test.xml`）で本番用設定を上書きするパターンが一般的。

参照:
- 日付管理
  .claude/skills/nabledge-6/docs/component/libraries/libraries-date.md
  システム日時(OS日時)と業務日付の切り替えができる
  システム日時の管理機能を使うための設定
  システム日時を切り替える
- 目的別API使用方法
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-03-Tips.md
  システム日時を任意の値に固定したい