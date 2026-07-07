# impact-08 — run-2

## 質問

テスト時だけシステム日時を任意の日付に差し替える方法はあるか？本番とテストで切り替えたい

## 回答

**結論**: テスト時のみシステム日時を固定値に差し替えるには、テスト用コンポーネント設定ファイルで `systemTimeProvider` に `FixedSystemTimeProvider` を設定し、本番用と切り替えます。

**根拠**:

Nablarchはシステム日時の提供を `SystemTimeProvider` インターフェースの実装クラスが担います。コンポーネント定義で指定するクラスを差し替えるだけで、本番とテストで異なる日時取得方法に切り替えることができます。

**テスト用コンポーネント設定ファイル（`src/test/resources` 内）：**

```xml
<component name="systemTimeProvider"
    class="nablarch.test.FixedSystemTimeProvider">
  <property name="fixedDate" value="20100913123456" />
</component>
```

| property名 | 設定内容 |
|---|---|
| fixedDate | 固定したい日時を `yyyyMMddHHmmss`（12桁）または `yyyyMMddHHmmssSSS`（15桁）形式で指定 |

**本番用コンポーネント設定ファイル：**

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

切り替えの仕組みは「環境ごとにコンポーネント設定ファイル（XMLファイル）を差し替える」パターンで実現します。テスト環境用の設定を `src/test/resources` に配置し、本番環境（`src/env/prod`）と別ファイルにしておくことで、ビルド時・テスト実行時に自動的に切り替わります。

アプリケーションコードからは `SystemTimeUtil` でシステム日時を取得します。

**注意点**: 独自クラスで切り替えたい場合は `SystemTimeProvider` インターフェースを実装したクラスを作成し、同じ `systemTimeProvider` という名前でコンポーネント定義に設定します。

参照: testing-framework-03-Tips.json:s11, testing-framework-03-Tips.json:s12, libraries-date.json:s2, libraries-date.json:s5, libraries-date.json:s12, setting-guide-ManagingEnvironmentalConfiguration.json:s9, setting-guide-ManagingEnvironmentalConfiguration.json:s10

## 参照ナレッジ

- [システム日時(OS日時)と業務日付の切り替えができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時os日時と業務日付の切り替えができる) (s2)
- [システム日時の管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時の管理機能を使うための設定) (s5)
- [システム日時を切り替える](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時を切り替える) (s12)
- [システム日時を任意の値に固定したい](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-03-Tips.md#システム日時を任意の値に固定したい) (s11)
- [設定ファイル例](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/development-tools/testing-framework/testing-framework-03-Tips.md#設定ファイル例) (s12)
- [環境ごとにコンポーネントを切り替える方法(モックに切り替える方法)](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.md#環境ごとにコンポーネントを切り替える方法モックに切り替える方法) (s9)
- [コンポーネント設定ファイル(xmlファイル)の作成方法](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/setup/setting-guide/setting-guide-ManagingEnvironmentalConfiguration.md#コンポーネント設定ファイルxmlファイルの作成方法) (s10)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the core fact in the Expected Output: that by replacing the class specified in the component definition, the system time acquisition method can be switched. The Actual Output explicitly states 'コンポーネント定義で指定するクラスを差し替えるだけで、本番とテストで異なる日時取得方法に切り替えることができます', which is equivalent to the expected fact, even providing additional detail about how this works in practice. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant to the question about how to replace the system date/time with an arbitrary date during testing and switch between production and test environments. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.93 | NG | The score is 0.93 because the actual output correctly references '20100913123456' as the example fixedDate value, consistent with the retrieval context. The minor contradiction lies in the date interpretation — the retrieval context associates '20100913123456' with September 14, 2010, while the value itself represents September 13, 2010, suggesting an internal inconsistency in the source material rather than a clear error in the actual output. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- コンポーネント定義で指定するクラスを差し替えることでシステム日時の取得方法を切り替えられる
