**結論**: テスト時だけシステム日時を固定するには、テスト用コンポーネント設定ファイルで `systemTimeProvider` を `FixedSystemTimeProvider` に差し替える。本番では `BasicSystemTimeProvider`（OS時刻）、テストでは `FixedSystemTimeProvider`（固定値）を使い分けることで切り替えが実現できる。

---

**根拠**:

Nablarchのシステム日時管理は `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で注入する仕組みになっている。コンポーネントを差し替えるだけで動作が切り替わるため、テストと本番で異なる実装を使用できる。

**本番環境の設定** (`src/main/resources/` 等):
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト環境の設定** (`src/test/resources/` 等でオーバーライド):
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

`fixedDate` プロパティに指定できるフォーマット:

| フォーマット | 桁数 |
|---|---|
| yyyyMMddHHmmss | 14桁 |
| yyyyMMddHHmmssSSS | 17桁 |

**切り替えの仕組み**: Nablarchのブランクプロジェクトはディレクトリ構成として `src/test/resources/` 配下のコンポーネント設定ファイルがユニットテスト時に使用される。`src/main/resources/` の設定を `src/test/resources/` 側で同名コンポーネントとして上書き定義すれば、テスト実行時のみ `FixedSystemTimeProvider` が使われる。

本番コードで日時を取得する側は `SystemTimeUtil` を使用しており、この実装クラスがどちらに設定されていても同じ呼び出し方で動作する。

---

**注意点**: `FixedSystemTimeProvider` は `nablarch-testing` モジュールに含まれるため、本番依存には含めず `test` スコープで依存関係に追加すること。

参照: `component/libraries/libraries-date.json:s2`, `component/libraries/libraries-date.json:s5`, `component/libraries/libraries-date.json:s12`, `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `development-tools/testing-framework/testing-framework-03-Tips.json:s12`

---