**結論**: テスト時のみシステム日時を固定値に差し替えるには、テスト用コンポーネント設定ファイルで `systemTimeProvider` に `FixedSystemTimeProvider` を設定し、本番用と切り替えます。

**根拠**:

Nablarchはシステム日時の提供を `SystemTimeProvider` インターフェースの実装クラスが担います。コンポーネント定義で指定するクラスを差し替えるだけで、本番とテストで異なる日時取得方法に切り替えることができます。

**テスト用コンポーネント設定ファイル（`src/test/resources` 内）：**

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 固定したい日時を `yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁）形式で指定 |

**本番用コンポーネント設定ファイル：**

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

切り替えの仕組みは「環境ごとにコンポーネント設定ファイル（XMLファイル）を差し替える」パターンで実現します。テスト環境用の設定を `src/test/resources` に配置し、本番環境（`src/env/prod`）と別ファイルにしておくことで、ビルド時・テスト実行時に自動的に切り替わります。

アプリケーションコードからは `SystemTimeUtil` でシステム日時を取得します。

**注意点**: 独自クラスで切り替えたい場合は `SystemTimeProvider` インターフェースを実装したクラスを作成し、同じ `systemTimeProvider` という名前でコンポーネント定義に設定します。

参照: testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12, setting-guide-ManagingEnvironmentalConfiguration.json:s9, setting-guide-ManagingEnvironmentalConfiguration.json:s10