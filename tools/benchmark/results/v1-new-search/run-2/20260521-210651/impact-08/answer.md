Step 4: セクションを読みました。Step 5で回答を生成します。

**read_sections:**
- `development-tools/testing-framework/testing-framework-03-Tips.json:s11`
- `development-tools/testing-framework/testing-framework-03-Tips.json:s12`
- `component/libraries/libraries-date.json:s2`
- `component/libraries/libraries-date.json:s5`
- `component/libraries/libraries-date.json:s12`
- `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s9`
- `setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.json:s10`

---

## 回答

**結論**: Nablarchでは `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで、本番とテストでシステム日時の取得方法を切り替えられます。テスト用クラス `FixedSystemTimeProvider` を使えば、任意の日時に固定できます。

**根拠**:

Nablarchのシステム日時管理は `SystemTimeProvider` インタフェースに基づいています。コンポーネント定義で指定するクラスを差し替えるだけで切り替えられます。

**本番環境の設定（通常はOS日時を使用）**:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト環境の設定（任意の日時に固定）**:

テスト用の `FixedSystemTimeProvider` を使い、`fixedDate` プロパティに固定したい日時を指定します。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 固定したい日時（`yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁）） |

**本番/テストの切り替え方法**:

コンポーネント設定ファイル（XML）を環境ごとに別ファイルとして作成し、Mavenプロファイルでビルド時に切り替えます。`src/env/dev/`（開発・テスト用）と `src/env/prod/`（本番用）にそれぞれ別の設定ファイルを配置することで、ビルド時に自動的に差し替えられます。

**注意点**: 独自の日時クラスが必要な場合（OS日時以外のソースや、毎回インクリメントするなど）は、`SystemTimeProvider` インタフェースを自作して設定します。

参照: `testing-framework-03-Tips.json:s11`, `testing-framework-03-Tips.json:s12`, `libraries-date.json:s2`, `libraries-date.json:s5`, `libraries-date.json:s12`

---