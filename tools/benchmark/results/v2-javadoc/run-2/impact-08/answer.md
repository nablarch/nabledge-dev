セクション内容を取得しました。Step 5〜8として回答を生成し検証します。

---

**結論**: テスト時だけシステム日時を固定値に差し替えるには、コンポーネント定義ファイルでテスト用の `FixedSystemTimeProvider` に切り替えます。本番では `BasicSystemTimeProvider`、テストでは `FixedSystemTimeProvider` をそれぞれのコンポーネント設定ファイルに指定することで、コード変更なしに切り替えが実現できます。

**根拠**:

Nablarchのシステム日時は `SystemTimeProvider` インタフェースを介して取得される仕組みになっており、コンポーネント定義で指定するクラスを差し替えるだけで取得方法を変更できます。

**本番環境の設定（BasicSystemTimeProvider）:**

```xml
<!-- OS のシステム日時をそのまま返す -->
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト環境の設定（FixedSystemTimeProvider）:**

```xml
<!-- 固定値を返すテスト用クラスに差し替える -->
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` のフォーマット:

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 14桁 |
| `yyyyMMddHHmmssSSS` | 17桁 |

**切り替えの仕組み:**

- Nablarchのブランクプロジェクトは環境ごとにコンポーネント設定ファイルを分けられるため（例: `src/main/resources/` と `src/test/resources/`）、テスト用設定ファイルで上書きするだけで切り替えが完結します。
- アプリケーション側は `SystemTimeUtil` 経由でシステム日時を取得し続けるだけでよく、取得側のコードは変更不要です。

**独自クラスで切り替えたい場合（より高度な制御）:**

`SystemTimeProvider` インタフェースを自分で実装し、コンポーネント定義でそのクラスを指定することも可能です（例: テストメソッドごとに日時を変えたい場合など）。

```java
// SystemTimeProvider インタフェース
Date getDate();
Timestamp getTimestamp();
```

**注意点**: テスト用設定ファイルは本番にデプロイされないよう、`src/test/resources/` 配下に配置すること。

参照: `development-tools/testing-framework/testing-framework-03-Tips.json:s11`, `testing-framework-03-Tips.json:s12`, `component/libraries/libraries-date.json:s2`, `libraries-date.json:s5`, `libraries-date.json:s12`

---