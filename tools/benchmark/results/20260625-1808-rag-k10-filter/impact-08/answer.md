はい、Nablarchにはテスト時にシステム日時を任意の値に差し替える仕組みが用意されています。

**仕組みの概要**

Nablarchのシステム日時は `SystemTimeProvider` インターフェースの実装クラスが提供します。コンポーネント定義でこの実装クラスを差し替えるだけで、本番とテストで異なる日時を使えます。

**本番時の設定**

コンポーネント定義に `BasicSystemTimeProvider` を指定します（OSの実際の日時を返します）。

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト時の設定**

テスト用コンポーネント定義で `FixedSystemTimeProvider` に差し替え、固定したい日時を指定します。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` には以下のフォーマットで指定できます。

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 14桁 |
| `yyyyMMddHHmmssSSS` | 17桁 |

**切り替えの仕組み**

- コンポーネント名 `systemTimeProvider` に登録するクラスを変えるだけで切り替わります
- 本番：`BasicSystemTimeProvider`（OS日時を返す）
- テスト：`FixedSystemTimeProvider`（固定値を返す）
- 独自の切り替えが必要な場合は、`SystemTimeProvider` を実装した独自クラスを作成して登録することも可能です

**自分で実装する場合**

`SystemTimeProvider` インターフェースを実装したクラスを作成し、上記と同様にコンポーネント定義へ登録するだけです。これにより、ランダムな日時や外部から注入する日時など、任意のロジックで日時を制御できます。

なお、Nablarch 6u2以降では `SystemTimeUtil` で `LocalDateTime` 型でのシステム日時取得にも対応しています（従来の `Date` 型に加えて）。