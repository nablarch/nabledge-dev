# review-08 — run-3

## 質問

入力→確認→完了画面間でセッション変数を保持するとき、DBストアとHIDDENストアの使い分けはどうすればいい？

## 回答

**結論**: 「複数タブでの画面操作を許容するか否か」で使い分けます。許容しない場合はDBストア、許容する場合はHIDDENストアを使用します。

**根拠**:

| 要件 | 選択するストア |
|------|--------------|
| 入力～確認～完了画面間（複数タブ不許容） | DBストア |
| 入力～確認～完了画面間（複数タブ許容） | HIDDENストア |

**DBストアの特徴（複数タブ不許容の場合）**:
- セッション変数をデータベース上のテーブルに保存する
- アプリケーションサーバが停止してもセッションの復元が可能
- 同一セッションが複数スレッドで処理された場合は後勝ち（先のデータは消失）

**HIDDENストアの特徴（複数タブ許容の場合）**:
- クライアントサイドで hidden タグを使って画面間でセッション変数を引き回す
- 複数タブでの画面操作を許容できる
- 同一セッションが複数スレッドで処理された場合も、各スレッドに紐付けて保存される

HIDDENストアを使用する場合、入力・確認画面のJSPに `hiddenStore` タグを追加します：

```jsp
<n:form>
  <!--
    name属性にはHiddenStoreのparameterNameプロパティの値を設定
  -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

**アクション側の実装（いずれのストアでも共通）**:

```java
// 入力画面→確認画面：入力情報をセッションストアに保存
ProjectForm form = context.getRequestScopedVar("form");
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 完了処理：セッションストアからデータを取得して登録
Project project = SessionUtil.get(ctx, "project");
// 登録処理は省略
SessionUtil.delete(ctx, "project");
```

**注意点**: セッションストアに保存するのは Form ではなく、業務ロジック用の Entity（登録・更新対象オブジェクト）にすることが推奨されています。Form を格納すると業務ロジックに不要な変換処理が入り込み、セキュリティ上もバリデーション前の信頼できない値をセッションに保持するリスクがあります。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-create-example.json:s2, libraries-create-example.json:s4

## 参照ナレッジ

- [入力～確認～完了画面間で入力情報を保持する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#入力確認完了画面間で入力情報を保持する) (s9)
- [セッションストアの特長と選択基準](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアの特長と選択基準) (s16)
- [セッション変数の保存先を選択できる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッション変数の保存先を選択できる) (s2)
- [セッションストアを使用するための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアを使用するための設定) (s8)
- [入力画面から確認画面へ遷移](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#入力画面から確認画面へ遷移) (s2)
- [登録処理を実行](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#登録処理を実行) (s4)
- [入力画面の初期表示](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#入力画面の初期表示) (s1)
- [制約](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/handlers/handlers-SessionStoreHandler.md#制約) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers the single fact in the Expected Output: that DBストア is used when multiple tab operations are not allowed, and HIDDENストア is used when they are allowed. This core distinction is explicitly stated in the conclusion section and reinforced throughout the response. The Actual Output goes well beyond the Expected Output with additional details, but the key expected fact is fully covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant to the question about how to differentiate between DB store and HIDDEN store when maintaining session variables across input, confirmation, and completion screens. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「複数タブ操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使う」は回答の結論「許容しない場合はDBストア、許容する場合はHIDDENストアを使用します」に明示されている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- 複数タブ操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使う
