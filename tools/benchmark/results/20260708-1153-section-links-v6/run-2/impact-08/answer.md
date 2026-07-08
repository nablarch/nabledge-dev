**結論**: テスト時だけシステム日時を任意の値に切り替えるには、コンポーネント定義で `systemTimeProvider` に指定するクラスを差し替えます。テスト時は `nablarch.test.FixedSystemTimeProvider`、本番では `nablarch.core.date.BasicSystemTimeProvider` を使うことで、設定ファイルの差し替えだけで切り替えが実現できます。

**根拠**:

Nablarchでは `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供します。コンポーネント定義で指定するクラスを差し替えるだけで取得方法を切り替えられるため、テスト用と本番用でそれぞれ別の設定ファイルを用意するのが基本的なアプローチです。

**本番用設定**:

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定（固定日時を返す）**:

`FixedSystemTimeProvider` を指定し、`fixedDate` プロパティに固定したい日時を設定します。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 指定したい日時（`yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁）） |

固定したシステム日時の取得方法:

```java
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**注意点**:
- `FixedSystemTimeProvider` はテスト用クラス（`nablarch.test` パッケージ）のため、本番コードには含めないこと。
- 本番とテストで異なるコンポーネント設定ファイルを使い分けることで切り替えを実現する。

参照:
- 日付管理
  .claude/skills/nabledge-6/docs/component/libraries/libraries-date.md
  システム日時(OS日時)と業務日付の切り替えができる
  システム日時の管理機能を使うための設定
  システム日時を切り替える
- 目的別API使用方法
  .claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-03-Tips.md
  システム日時を任意の値に固定したい
  設定ファイル例