# impact-08 — run-3

## 質問

テスト時だけシステム日時を任意の日付に差し替える方法はあるか？本番とテストで切り替えたい

## 回答

**結論**: Nablarchの日付管理機能では、コンポーネント定義に指定するクラスを差し替えるだけでシステム日時を切り替えられる。テスト用には `SystemTimeProvider` インターフェースを実装したクラスを作り、テスト環境のコンポーネント定義で `systemTimeProvider` として登録することで、任意の日時を返すよう切り替えられる。

---

**根拠**:

**仕組み**

アプリケーションは `SystemTimeUtil` 経由でシステム日時を取得するが、実際の取得処理は `systemTimeProvider` という名前でコンポーネント定義に登録されたクラス（`SystemTimeProvider` インターフェースの実装）に委譲される。コンポーネント定義で指定するクラスを差し替えるだけで取得方法が切り替わる。

**本番環境の設定（OS日時を返す）**

```xml
<component name="systemTimeProvider" class="nablarch.core.date.BasicSystemTimeProvider" />
```

**テスト環境への切り替え手順**

1. `SystemTimeProvider` インターフェースを実装したクラスを作成する（任意の日時を返す実装）
2. テスト用コンポーネント定義ファイルで、そのクラスを `systemTimeProvider` として設定する

---

**業務日付も同様の仕組み**

業務日付（`BusinessDateUtil` 経由で取得）も同じ方式で切り替えられる。

1. `BusinessDateProvider` インターフェースを実装したクラスを作成する
2. テスト用コンポーネント定義で `businessDateProvider` として設定する

本番環境では `BasicBusinessDateProvider`（DBのテーブルから取得）が使われるが、テスト用の実装に差し替えることで任意の日付を返せる。

---

**注意点**: この切り替えはコンポーネント定義ファイルの差し替えで実現するため、テスト実行時にテスト用コンポーネント定義が読み込まれる構成にする必要がある。

参照: component/libraries/libraries-date.json:s2, s5, s6, s12, s13

## 参照ナレッジ

- [システム日時(OS日時)と業務日付の切り替えができる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時os日時と業務日付の切り替えができる) (s2)
- [システム日時を切り替える](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時を切り替える) (s12)
- [業務日付を切り替える](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を切り替える) (s13)
- [システム日時の管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時の管理機能を使うための設定) (s5)
- [システム日時を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#システム日時を取得する) (s6)
- [業務日付管理機能を使うための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付管理機能を使うための設定) (s7)
- [業務日付を取得する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-date.md#業務日付を取得する) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly states that system date/time can be switched by replacing the class specified in the component definition ('コンポーネント定義で指定するクラスを差し替えるだけで取得方法が切り替わる'), which directly covers the single expected fact. The coverage is complete. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant to the question about how to replace the system date/time with an arbitrary date during testing and switch between production and test environments. No irrelevant statements were identified! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「コンポーネント定義で指定するクラスを差し替えることでシステム日時の取得方法を切り替えられる」は回答の「コンポーネント定義で指定するクラスを差し替えるだけで取得方法が切り替わる」に含まれている |
| answer_relevancy | NG | 「参照: component/libraries/libraries-date.json:s2, s5, s6, s12, s13」という内部参照記法がユーザー向け回答の末尾に含まれており不適切 |
| faithfulness | OK | ナレッジ内容と矛盾なし（SystemTimeProviderの実装・systemTimeProviderコンポーネント名・BasicSystemTimeProvider・BusinessDateProvider・BasicBusinessDateProviderのDB参照すべてナレッジと一致） |

### 参照事実（expected_facts）

- コンポーネント定義で指定するクラスを差し替えることでシステム日時の取得方法を切り替えられる
