はい、テスト時にシステム日時を任意の値に固定する仕組みが用意されています。

**仕組みの概要**

Nablarch では `SystemTimeProvider` インターフェースの実装クラスがシステム日時を提供します。コンポーネント定義でこの実装クラスを差し替えるだけで、本番とテストでシステム日時の取得方法を切り替えられます。

- **本番環境**: `BasicSystemTimeProvider`（OS のシステム日時を返す）
- **テスト環境**: `FixedSystemTimeProvider`（固定値を返すテスト用クラス）

**テスト用の設定例**

テスト用のコンポーネント設定ファイルで `FixedSystemTimeProvider` を指定し、固定したい日時をプロパティに設定します。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

| プロパティ名 | 設定内容 |
|---|---|
| `fixedDate` | `yyyyMMddHHmmss`（14桁）または `yyyyMMddHHmmssSSS`（17桁）形式の文字列 |

**本番用の設定例**

```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**切り替えの流れ**

1. 本番用とテスト用でコンポーネント定義ファイルを分ける
2. テスト用ファイルで `systemTimeProvider` の実装クラスを `FixedSystemTimeProvider` に差し替える
3. アプリケーションコードは `SystemTimeProvider` インターフェース経由でシステム日時を取得するため、設定の差し替えだけで動作が変わる

これにより、登録日時・更新日時のように実行日によって値が変わる項目も、固定値でテストを安定させることができます。

なお、Nablarch 6u2 以降では `SystemTimeUtil` を使って `LocalDateTime` 型でのシステム日時取得にも対応しています。