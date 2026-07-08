# impact-08 — run-1

## 質問

テスト時だけシステム日時を任意の日付に差し替える方法はあるか？本番とテストで切り替えたい

## 回答

**結論**: Nablarchでは `SystemTimeProvider` インタフェースの実装クラスをコンポーネント定義で差し替えることで、本番とテストのシステム日時を切り替えられます。テスト用には `nablarch.test.FixedSystemTimeProvider` を使い、任意の固定日時を設定します。

**根拠**:

**仕組み**

アプリケーションは `systemTimeProvider` という名前のコンポーネントを通じてシステム日時を取得します。コンポーネント定義で指定するクラスを差し替えるだけで、日時の取得方法を切り替えられます。

**本番用設定** (`src/main/resources/` などの本番用設定ファイル):

```xml
<component name="systemTimeProvider"
    class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト用設定** (`src/test/resources/` などのテスト用設定ファイル):

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100914123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| `fixedDate` | 固定したい日時を `yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁）形式で指定 |

**アプリケーションコードでのシステム日時取得** (変更不要):

```java
// SystemTimeUtil を通じて取得。本番/テストどちらの設定でも同じ呼び出しで動作する
SystemTimeProvider provider = (SystemTimeProvider) SystemRepository.getObject("systemTimeProvider");
Date now = provider.getDate();
```

**切り替えの実現方法**

Maven プロファイルを使い、環境別ディレクトリ (`src/env/dev/`, `src/env/prod/` など) にそれぞれのコンポーネント設定ファイルを配置します。ユニットテスト実行時は `src/test/resources/` 配下の設定ファイルが使われるため、そちらに `FixedSystemTimeProvider` を定義します。

**注意点**:
- `FixedSystemTimeProvider` は `nablarch-testing` モジュールに含まれます。テストスコープ（`<scope>test</scope>`）で依存関係に追加する必要があります。
- 独自の切り替えロジックが必要な場合は、`SystemTimeProvider` インタフェースを独自実装して設定することもできます。

参照: libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s6, libraries-date.json:s12, testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12

## 参照ナレッジ

- [システム日時(OS日時)と業務日付の切り替えができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時os日時と業務日付の切り替えができる) (s2)
- [システム日時の管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時の管理機能を使うための設定) (s5)
- [システム日時を切り替える](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時を切り替える) (s12)
- [システム日時を任意の値に固定したい](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-03-Tips.md#システム日時を任意の値に固定したい) (s11)
- [設定ファイル例](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-03-Tips.md#設定ファイル例) (s12)
- [システム日時を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時を取得する) (s6)
- [業務日付を切り替える](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を切り替える) (s13)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly covers the expected fact: 'コンポーネント定義で指定するクラスを差し替えることでシステム日時の取得方法を切り替えられる'. This is stated clearly in the '仕組み' section: 'コンポーネント定義で指定するクラスを差し替えるだけで、日時の取得方法を切り替えられます。' The single expected fact is fully covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing how to replace the system date/time with an arbitrary date during testing and how to switch between production and test environments. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.93 | NG | The score is 0.93 because the actual output contains one contradiction: it incorrectly states the fixedDate example value as '20100914123456' (September 14), whereas the retrieval context specifies the correct value should be '20100913123456' (September 13) to represent September 14, 2010, 12:34:56. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「コンポーネント定義で指定するクラスを差し替えることでシステム日時の取得方法を切り替えられる」は回答の「コンポーネント定義で指定するクラスを差し替えるだけで、日時の取得方法を切り替えられます。」に含まれている |
| answer_relevancy | OK | 回答はテスト時のシステム日時の差し替え方法と本番/テストの切り替え方法という質問に直接答えている。SystemTimeProviderの仕組み、本番用設定（BasicSystemTimeProvider）、テスト用設定（FixedSystemTimeProvider）、Mavenプロファイルを使った切り替え方法、注意点まですべて質問に関連する内容であり、的外れな情報は含まれていない。 |
| faithfulness | OK | サンプルのfixedDate値（`20100914123456`）はナレッジの例（`20100913123456`）と日付が1日異なるが、この値は形式例（`yyyyMMddHHmmss`）であり特定の日付に意味はない。回答のSystemTimeProvider設定・使用方法はナレッジと矛盾しない。 |

### 参照事実（expected_facts）

- コンポーネント定義で指定するクラスを差し替えることでシステム日時の取得方法を切り替えられる
