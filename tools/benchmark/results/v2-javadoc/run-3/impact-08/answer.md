Step 5: 回答を生成します。

**answer_text:**

---

**結論**: テスト時だけシステム日時を固定値に差し替えるには、テスト用コンポーネント定義で `systemTimeProvider` を `nablarch.test.FixedSystemTimeProvider` に差し替えます。本番では `BasicSystemTimeProvider`（OS時刻を返す）、テストでは `FixedSystemTimeProvider`（固定値を返す）と、コンポーネント定義ファイルを環境ごとに切り替えることで実現します。

**根拠**:

Nablarchのシステム日時取得は `SystemTimeProvider` インタフェース経由で行われます。本番用の設定では `BasicSystemTimeProvider` を `systemTimeProvider` という名前でコンポーネント定義します：

```xml
<!-- 本番用 -->
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

テスト用の設定ファイルでは、このコンポーネントを `FixedSystemTimeProvider` で上書きします。`fixedDate` プロパティに固定したい日時を設定します：

```xml
<!-- テスト用 -->
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` に指定するフォーマットは以下のいずれかです：

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 12桁 |
| `yyyyMMddHHmmssSSS` | 15桁 |

**切り替えの仕組み**: コンポーネント定義ファイルはMavenプロファイルによって環境ごとに切り替わります。テスト実行時 (`mvn test`) は `src/test/resources` 以下のリソースが使われるため、本番用ファイルとは独立したテスト用コンポーネント定義を `src/test/resources` に配置するだけで自動的に差し替わります。

なお、`FixedSystemTimeProvider` では要件を満たせない場合（例: テストシナリオごとに異なる日時を返したい）は、`SystemTimeProvider` インタフェースを独自に実装して使用することもできます。

**注意点**:
- アプリケーションコード側は `SystemTimeProvider` を直接使わず、`SystemTimeUtil` 経由で取得することが前提です。`new Date()` や `LocalDateTime.now()` を直接呼ぶと、このコンポーネント差し替えの仕組みが効きません。

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12, testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, setting-guide-ManagingEnvironmentalConfiguration.json:s9, setting-guide-ManagingEnvironmentalConfiguration.json:s10

---

Step 6: Verify実施します。

抽出するNablarch固有のクレーム：
1. `SystemTimeProvider` インタフェース経由でシステム日時取得 → s11で「SystemTimeProviderインタフェースの実装クラスがシステム日時を提供する」と明記 ✅
2. `BasicSystemTimeProvider` が本番実装 → s5で「BasicSystemTimeProviderの設定をコンポーネント定義に追加する」と明記 ✅
3. コンポーネント名 `systemTimeProvider` → s5で「コンポーネント名にはsystemTimeProviderと指定する」と明記 ✅
4. `nablarch.test.FixedSystemTimeProvider` → s12の設定例に `class="nablarch.test.FixedSystemTimeProvider"` と明記 ✅
5. `fixedDate` プロパティ → s12に明記 ✅
6. フォーマット `yyyyMMddHHmmss`(12桁) / `yyyyMMddHHmmssSSS`(15桁) → s12に明記 ✅
7. Mavenプロファイルで環境ごとに切り替え → s7, s8で明記、`src/test/resources`はs8で明記 ✅
8. `SystemTimeUtil` 経由での取得推奨 → s6で「システム日時の取得は、SystemTimeUtilを使用する」と明記 ✅（ただし注意点での「直接呼ぶと効かない」部分は一般的なJava知識であり、Nablarch固有の仕様として明記はされていないが、仕組みの論理的帰結）

`verify_result = PASS`

Step 8: 回答を出力します。

---

**結論**: テスト時だけシステム日時を固定値に差し替えるには、テスト用コンポーネント定義で `systemTimeProvider` を `nablarch.test.FixedSystemTimeProvider` に差し替えます。本番では `BasicSystemTimeProvider`（OS時刻を返す）、テストでは `FixedSystemTimeProvider`（固定値を返す）と、コンポーネント定義ファイルを環境ごとに切り替えることで実現します。

**根拠**:

Nablarchのシステム日時取得は `SystemTimeProvider` インタフェース経由で行われます。本番用の設定では `BasicSystemTimeProvider` を `systemTimeProvider` という名前でコンポーネント定義します：

```xml
<!-- 本番用 -->
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

テスト用の設定ファイルでは、このコンポーネントを `FixedSystemTimeProvider` で上書きします。`fixedDate` プロパティに固定したい日時を設定します：

```xml
<!-- テスト用 -->
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` に指定するフォーマットは以下のいずれかです：

| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 12桁 |
| `yyyyMMddHHmmssSSS` | 15桁 |

**切り替えの仕組み**: コンポーネント定義ファイルはMavenプロファイルによって環境ごとに切り替わります。テスト実行時 (`mvn test`) は `src/test/resources` 以下のリソースが使われるため、本番用ファイルとは独立したテスト用コンポーネント定義を `src/test/resources` に配置するだけで自動的に差し替わります。

なお、`FixedSystemTimeProvider` では要件を満たせない場合（例: テストシナリオごとに異なる日時を返したい場合）は、`SystemTimeProvider` インタフェースを独自に実装して使用することもできます。

**注意点**:
- アプリケーションコード側は `SystemTimeUtil` を使ってシステム日時を取得することが前提です。`new Date()` や `LocalDateTime.now()` を直接呼ぶと、このコンポーネント差し替えの仕組みが効きません。

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12, testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, setting-guide-ManagingEnvironmentalConfiguration.json:s9, setting-guide-ManagingEnvironmentalConfiguration.json:s10

---