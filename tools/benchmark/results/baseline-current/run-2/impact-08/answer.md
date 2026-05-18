**結論**: はい、可能です。Nablarch の日付管理機能は `SystemTimeProvider` インタフェースを介してシステム日時を取得する設計になっており、コンポーネント定義で指定するクラスを差し替えるだけで本番とテストを切り替えられます。

**根拠**:

**本番環境の設定**

コンポーネント定義に `BasicSystemTimeProvider` を登録します（コンポーネント名は `systemTimeProvider` 固定）。

```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

システム日時の取得には `SystemTimeUtil` を使用します。

**テスト時の設定（日時を固定値に差し替える）**

テスティングフレームワークが提供する `FixedSystemTimeProvider` を使用し、コンポーネント定義の `systemTimeProvider` を上書きします。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` プロパティには以下のいずれかのフォーマットで日時を指定します。

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 14桁 |
| `yyyyMMddHHmmssSSS` | 17桁 |

**完全なカスタム実装が必要な場合**

任意のロジックでシステム日時を返したい場合は、`SystemTimeProvider` インタフェースを実装したクラスを作成し、テスト用コンポーネント定義で差し替えます。

1. `SystemTimeProvider` を実装したクラスを作成する
2. テスト用コンポーネント定義の `systemTimeProvider` にそのクラスを指定する

**注意点**:

- `FixedSystemTimeProvider` はテスティングフレームワーク（`nablarch-test` モジュール）が提供するクラスです。本番コードには含めないようにしてください（`test` スコープの依存として管理します）。
- コンポーネント名は必ず `systemTimeProvider` にする必要があります。別の名前にすると `SystemTimeUtil` が参照できません。
- 業務日付（`BusinessDateUtil`）を固定したい場合は、`BusinessDateProvider` インタフェースを実装したクラスを同様の手順で差し替えます。

参照: `libraries-date.json#s2`, `libraries-date.json#s5`, `libraries-date.json#s12`, `testing-framework-03-Tips.json#s11`, `testing-framework-03-Tips.json#s12`