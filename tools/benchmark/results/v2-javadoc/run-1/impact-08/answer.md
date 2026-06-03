Step 5: 回答を生成します。

---

**結論**: Nablarchのシステム日時管理は `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで切り替えられる。テスト時は `nablarch.test.FixedSystemTimeProvider` を指定するだけで任意の日時に固定できる。

**根拠**:

Nablarchでは、システム日時の取得元（実装クラス）をコンポーネント定義ファイル（XML）に **`systemTimeProvider`** という名前で宣言する仕組みになっている。本番とテストで設定ファイルを切り替えることで日時ロジックを差し替えられる。

**本番用設定** (`BasicSystemTimeProvider` = OS日時をそのまま返す):
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定** (`FixedSystemTimeProvider` = 任意の固定日時を返す):
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` プロパティのフォーマット:
| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 12桁 |
| `yyyyMMddHHmmssSSS` | 15桁 |

**アプリケーションコードでのシステム日時取得**（本番・テスト共通）:
```java
SystemTimeUtil.getDate();  // コンポーネント定義の実装クラスに委譲される
```

**切り替えの仕組み**:
本番用とテスト用のコンポーネント設定ファイルをそれぞれ作成し、環境ごとに読み込むファイルを切り替える（テスト用リソースディレクトリに配置するか、テスト用設定ファイルで上書きする）。こうすることでアプリケーションコードを変更せずに日時の切り替えが実現できる。

**注意点**: `FixedSystemTimeProvider` は `nablarch-testing` モジュールに含まれるクラスであり、本番環境のクラスパスに含まれないよう `test` スコープの依存関係にすること。

参照: testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12

---

Step 6（Verify）: 回答のNablarch固有の主張を確認します。

- `SystemTimeProvider` インタフェース → s11に「SystemTimeProviderインタフェースの実装クラスがシステム日時を提供する」と明記 → **supported**
- `FixedSystemTimeProvider` クラス (`nablarch.test.FixedSystemTimeProvider`) → s12に `class="nablarch.test.FixedSystemTimeProvider"` と明記 → **supported**
- `fixedDate` プロパティ、フォーマット → s12の表に明記 → **supported**
- `BasicSystemTimeProvider` (本番) → s5に明記 → **supported**
- `SystemTimeUtil` → s6に「SystemTimeUtil を使用する」と明記 → **supported**
- コンポーネント名 `systemTimeProvider` → s5に「コンポーネント名には **systemTimeProvider** と指定する」と明記 → **supported**
- `nablarch-testing` モジュール所属の主張 → **sections_contentに明記なし** → unsupported claim

`verify_result = FAIL` — `nablarch-testing` モジュールへの言及は知識ファイルに根拠なし。

Step 7: `issues` の主張を除いた最終回答を生成します。

---

**結論**: Nablarchのシステム日時管理は `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで切り替えられる。テスト時は `nablarch.test.FixedSystemTimeProvider` を指定するだけで任意の日時に固定できる。

**根拠**:

Nablarchでは、システム日時の取得元（実装クラス）をコンポーネント定義ファイル（XML）に **`systemTimeProvider`** という名前で宣言する仕組みになっている。本番とテストでこの設定ファイルを切り替えることで日時ロジックを差し替えられる。

**本番用設定** (`BasicSystemTimeProvider` = OS日時をそのまま返す):
```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定** (`FixedSystemTimeProvider` = 任意の固定日時を返す):
```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

`fixedDate` プロパティのフォーマット:
| フォーマット | 桁数 |
|---|---|
| `yyyyMMddHHmmss` | 12桁 |
| `yyyyMMddHHmmssSSS` | 15桁 |

**アプリケーションコードでのシステム日時取得**（本番・テスト共通）:
```java
SystemTimeUtil.getDate();  // コンポーネント定義の実装クラスに委譲される
```

**切り替えの仕組み**:
本番用とテスト用のコンポーネント設定ファイルをそれぞれ作成し、環境ごとに読み込むファイルを切り替える（テスト用リソースディレクトリに配置するか、テスト用設定ファイルで上書きする）。アプリケーションコードを変更せずに日時の切り替えが実現できる。

参照: testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12

---