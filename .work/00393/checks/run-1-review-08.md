# review-08 — run-1

## 質問

入力→確認→完了画面間でセッション変数を保持するとき、DBストアとHIDDENストアの使い分けはどうすればいい？

## 回答

**結論**: 複数タブでの画面操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使用する。これが入力～確認～完了画面間でのセッション変数保持におけるストア選択の基準です。

**根拠**:

セッションストアの選択基準（`セッションストアの特長と選択基準` より）:

| 用途 | セッションストア |
|---|---|
| 入力～確認～完了画面間で入力情報の保持（**複数タブ不可**） | **DBストア** |
| 入力～確認～完了画面間で入力情報の保持（**複数タブ許容**） | **HIDDENストア** |

各ストアの特長:

**DBストア**（データベース上のテーブルに保存）
- ローリングメンテナンス等でAPサーバが停止してもセッション変数の復元が可能
- APサーバのヒープを圧迫しない
- 同一セッションが複数スレッドで実行された場合は**後勝ち**（先に保存されたデータは消失）

**HIDDENストア**（クライアントサイドのhiddenタグで引き回す）
- **複数タブでの画面操作を許容できる**
- APサーバのヒープを圧迫しない
- 同一セッションの複数スレッド実行時、データはそれぞれのスレッドに紐付けて保存される

HIDDENストアを使用する場合は、入力・確認画面のJSPに `hiddenStore` タグが必要です:

```jsp
<n:form>
  <!--
    name属性にはコンポーネント設定ファイルで定義した
    HiddenStoreのparameterNameプロパティの値を設定
  -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

セッション変数の読み書きは `SessionUtil` を使います（実装例より）:

```java
// 入力→確認遷移時: FormからEntityへ変換してセッションに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認→戻る時: セッションから取り出してFormに戻す
Project project = SessionUtil.get(ctx, "project");
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);
SessionUtil.delete(ctx, "project");

// 登録処理時: セッションから取り出して業務ロジックに使用し、削除
Project project = SessionUtil.get(ctx, "project");
// 登録処理...
SessionUtil.delete(ctx, "project");
```

**注意点**:
- セッションストアにはFormではなくEntity（業務ロジック用オブジェクト）を格納すること。Formを格納すると不要な変換処理が業務ロジックに混入しやすくなり、セキュリティの観点からも信頼できない値を長期保持するリスクがある
- HIDDENストアはデータが暗号化されてクライアントに送信されるが、アプリケーションサーバが冗長化されている場合はサーバ間で共通の暗号化キーを明示的に設定する必要がある（デフォルトではサーバごとにキーが自動生成されるため）
- セッションを使用し始める際は、入力画面の初期表示時に `SessionUtil.delete(ctx, "project")` で以前のセッションを削除しておくこと（ブラウザを直接閉じた場合などに残存している可能性があるため）

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-session-store.json:s12, libraries-create-example.json:s1, libraries-create-example.json:s2, libraries-create-example.json:s3, libraries-create-example.json:s4

## 参照ナレッジ

- [入力～確認～完了画面間で入力情報を保持する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#入力確認完了画面間で入力情報を保持する) (s9)
- [セッションストアの特長と選択基準](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアの特長と選択基準) (s16)
- [セッション変数の保存先を選択できる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッション変数の保存先を選択できる) (s2)
- [HIDDENストアの暗号化設定をカスタマイズする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#hiddenストアの暗号化設定をカスタマイズする) (s12)
- [入力画面の初期表示](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#入力画面の初期表示) (s1)
- [入力画面から確認画面へ遷移](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#入力画面から確認画面へ遷移) (s2)
- [確認画面から入力画面へ戻る](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#確認画面から入力画面へ戻る) (s3)
- [登録処理を実行](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#登録処理を実行) (s4)
- [セッションストアを使用するための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-SessionStoreHandler.md#セッションストアを使用するための設定) (s4)
- [セッションストアを使用するための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアを使用するための設定) (s8)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers the key fact from the Expected Output: that DBストア should be used when multiple tab operations are not allowed, and HIDDENストア should be used when they are allowed. This core information is clearly presented in the conclusion and in the table. The Actual Output provides significantly more detail than the Expected Output, but all expected facts are present and accurately conveyed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is fully relevant to the input, which asks about how to properly use DB store vs HIDDEN store when maintaining session variables across input, confirmation, and completion screens. No irrelevant statements were found — great job staying focused and on-topic! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- 複数タブ操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使う
