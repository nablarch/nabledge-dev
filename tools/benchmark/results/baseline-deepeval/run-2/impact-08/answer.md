Step 5: セクション内容をもとに回答を生成します。

**結論**: テスト時は `FixedSystemTimeProvider`（固定値を返すテスト用クラス）を `systemTimeProvider` コンポーネントに差し替えることで、任意のシステム日時を返せる。本番とテストの切り替えは、コンポーネント設定XMLファイルを環境ごとに用意してビルド時に差し替える仕組みで実現する。

**根拠**:

Nablarch では `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供する。コンポーネント定義で指定するクラスを差し替えるだけで日時取得方法を切り替えられる。

**本番環境**: OSの時刻を返す `BasicSystemTimeProvider` を使用する。

```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト時**: `FixedSystemTimeProvider` に差し替え、`fixedDate` プロパティに固定したい日時を設定する。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` に指定できるフォーマット:
- `yyyyMMddHHmmss`（14桁）
- `yyyyMMddHHmmssSSS`（17桁）

**本番/テスト切り替えの仕組み**:

コンポーネント設定XMLファイルを環境ごとに作成し、環境ごとのディレクトリに配置してビルド時に差し替える。ユニットテスト実行時はデフォルトで `dev` プロファイルが適用され、`src/test/resources` のリソースが使われるため、テスト用コンポーネント定義をそこに配置することで自動的に切り替わる。

**注意点**:
- `FixedSystemTimeProvider` は `nablarch.test` パッケージに属するテスト用クラスであり、本番コードには含めないこと。
- 業務日付（`BusinessDateProvider`）も同様に差し替え可能。テスト時は `BusinessDateProvider` を実装したクラスに切り替える。

参照: testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-date.json:s2, libraries-date.json:s5, setting-guide-ManagingEnvironmentalConfiguration.json:s9, setting-guide-ManagingEnvironmentalConfiguration.json:s10, setting-guide-ManagingEnvironmentalConfiguration.json:s8

---

Step 6: Verifyを実行します。

Nablarch固有のクレームを確認:
- `FixedSystemTimeProvider` → s12で明示 ✅
- `nablarch.test.FixedSystemTimeProvider` → s12で明示 ✅
- `fixedDate` プロパティ → s12で明示 ✅
- `BasicSystemTimeProvider` → s5で明示 ✅
- `SystemTimeProvider` インタフェース → s11, s12で明示 ✅
- `src/test/resources` / devプロファイル → s8で明示 ✅
- コンポーネント設定XMLを環境ごとに作成してビルド時差し替え → s10で明示 ✅
- 業務日付（`BusinessDateProvider`）も同様 → s13で明示 ✅

`verify_result = PASS`

---

**結論**: テスト時は `FixedSystemTimeProvider`（固定値を返すテスト用クラス）を `systemTimeProvider` コンポーネントに差し替えることで、任意のシステム日時を返せる。本番とテストの切り替えは、コンポーネント設定XMLファイルを環境ごとに用意してビルド時に差し替える仕組みで実現する。

**根拠**:

Nablarch では `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供する。コンポーネント定義で指定するクラスを差し替えるだけで日時取得方法を切り替えられる。

**本番環境**: OSの時刻を返す `BasicSystemTimeProvider` を使用する。

```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト時**: `FixedSystemTimeProvider` に差し替え、`fixedDate` プロパティに固定したい日時を設定する。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` に指定できるフォーマット:
- `yyyyMMddHHmmss`（14桁）
- `yyyyMMddHHmmssSSS`（17桁）

**本番/テスト切り替えの仕組み**:

コンポーネント設定XMLファイルを環境ごとに作成し、環境ごとのディレクトリに配置してビルド時に差し替える。ユニットテスト実行時はデフォルトで `dev` プロファイルが適用され、`src/test/resources` のリソースが使われるため、テスト用コンポーネント定義をそこに配置することで自動的に切り替わる。

**注意点**:
- `FixedSystemTimeProvider` は `nablarch.test` パッケージに属するテスト用クラスであり、本番コードには含めないこと。
- 業務日付（`BusinessDateProvider`）も同様の仕組みで差し替え可能。

参照: testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-date.json:s2, libraries-date.json:s5, setting-guide-ManagingEnvironmentalConfiguration.json:s9, setting-guide-ManagingEnvironmentalConfiguration.json:s10, setting-guide-ManagingEnvironmentalConfiguration.json:s8

---