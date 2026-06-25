テスト時のみシステム日時を差し替える仕組みが Nablarch に用意されています。

---

**仕組みの概要**

Nablarch では `SystemTimeProvider` インタフェースの実装クラスがシステム日時を提供します。コンポーネント定義でこの実装クラスを差し替えるだけで、本番とテストのシステム日時取得を切り替えられます。

---

**本番環境の設定**

本番では `BasicSystemTimeProvider`（OS のリアル日時を返す）をコンポーネント定義に登録します。コンポーネント名は `systemTimeProvider` と指定します。

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

---

**テスト環境の設定**

テスト用コンポーネント設定ファイルで、同じ名前 `systemTimeProvider` に対して `FixedSystemTimeProvider`（固定値を返すテスト用クラス）を指定します。`fixedDate` プロパティに返したい日時を設定します。

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` に指定できるフォーマットは以下の2種類です。

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 14桁 |
| `yyyyMMddHHmmssSSS` | 17桁 |

---

**切り替えの流れ**

1. `SystemTimeProvider` を実装したカスタムクラスを作成（既製の `FixedSystemTimeProvider` を使えば実装不要）
2. テスト用コンポーネント設定ファイルで `systemTimeProvider` を `FixedSystemTimeProvider` に差し替える
3. テスト実行時はその設定ファイルが読み込まれ、固定日時が返される

アプリケーションコードは `SystemRepository.getObject("systemTimeProvider")` で取得した `SystemTimeProvider` を使うため、**コードを変更せず設定ファイルの差し替えだけで切り替えが完結します**。

---

**補足**

- Nablarch 6u2 以降では `SystemTimeUtil` を通じて `LocalDateTime` 型でもシステム日時を取得できます（従来の `Date` 型に加えて対応）。
- 業務日付（`BusinessDateProvider`）も同様の仕組みで切り替えが可能です。