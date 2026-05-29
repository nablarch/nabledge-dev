**結論**: Nablarchには本番とテストでシステム日時を切り替える仕組みが標準で備わっており、**コンポーネント定義ファイルで `systemTimeProvider` に設定するクラスを差し替えるだけ**で切り替えられます。テスト用には `nablarch.test.FixedSystemTimeProvider` が提供されており、任意の日時に固定できます。

---

**根拠**:

Nablarchのシステム日時管理は `SystemTimeProvider` インタフェースで抽象化されています。

**本番用設定（`BasicSystemTimeProvider` = OS日時を使用）**:
```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定（`FixedSystemTimeProvider` = 任意の日時に固定）**:
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| `fixedDate` | `yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁）形式で指定 |

テスト用コンポーネント設定ファイルで上記のように `systemTimeProvider` コンポーネントを上書きすることで、テスト時だけ日時を固定できます。本番コードは `SystemTimeUtil` で日時を取得しており、差し替えても一切変更不要です。

より高度な制御が必要な場合（日時を動的に変化させたいなど）は、`SystemTimeProvider` インタフェースを自前で実装し、テスト用コンポーネント設定ファイルに登録することも可能です。

**注意点**: テスト設定ファイルでコンポーネントを上書きする方法については、Nablarchの環境設定切り替え機能（コンポーネント定義ファイルの分割と上書き）を利用します。テスト専用のxmlファイルで本番設定のコンポーネント名 `systemTimeProvider` を再定義するだけで切り替わります。

参照: `libraries-date.json:s2`, `libraries-date.json:s5`, `libraries-date.json:s12`, `testing-framework-03-Tips.json:s11`, `testing-framework-03-Tips.json:s12`

---