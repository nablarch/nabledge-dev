# review-08 — run-2

## 質問

入力→確認→完了画面間でセッション変数を保持するとき、DBストアとHIDDENストアの使い分けはどうすればいい？

## 回答

**結論**: 複数タブでの画面操作を許容しない場合は **DBストア**、複数タブを許容する場合は **HIDDENストア** を使用します。

**根拠**:

Nablarchのドキュメントでは、入力→確認→完了画面間のセッション変数保持について、以下の基準で使い分けることが規定されています。

| 用途 | 使用するストア |
|---|---|
| 複数タブでの画面操作を許容しない | **DBストア** |
| 複数タブでの画面操作を許容する | **HIDDENストア** |

**DBストアの特長**:
- データベース上のテーブルにセッション変数を保存する
- ローリングメンテナンス等でAPサーバが停止してもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合は後勝ち（先に保存されたデータは消失）

**HIDDENストアの特長**:
- クライアントサイドに `hidden` タグを使って画面間でセッション変数を引き回す
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 各スレッドに紐付けて保存されるため、複数スレッド実行時もデータが混在しない

**HIDDENストアを使う場合のJSP実装**:

```jsp
<n:form>
  <!--
    name属性にはコンポーネント設定ファイルに定義した、
    HiddenStoreのparameterNameプロパティの値を設定
  -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

**セッションストアへの保存・取得の実装例**（入力→確認画面遷移時）:

```java
// リクエストスコープから入力情報を取得
ProjectForm form = context.getRequestScopedVar("form");

// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

**確認→入力画面へ戻る場合**:

```java
// セッションストアから入力情報を取得
Project project = SessionUtil.get(ctx, "project");

// EntityからFormへ変換
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);

// 入力情報をリクエストスコープに設定
context.setRequestScopedVar("form", form);

// セッションストアから入力情報を削除
SessionUtil.delete(ctx, "project");
```

**注意点**:
- セッションストアには Form ではなく Entity（業務ロジックを実行するオブジェクト）を格納すること。Form を格納すると業務ロジックに不要なデータ変換処理が混入し、密結合なソースが生まれる可能性がある。
- HIDDENストアはデフォルトで AES 暗号化が適用される。APサーバを冗長化している場合は、復号失敗を防ぐために暗号化キーを明示的に設定すること。
- DBストアを使用する場合、`USER_SESSION` テーブルの作成が必要。また期限切れのセッション情報を定期的に削除する必要がある。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s8, libraries-session-store.json:s12, libraries-create-example.json:s1, libraries-create-example.json:s2, libraries-create-example.json:s3

## 参照ナレッジ

- [入力～確認～完了画面間で入力情報を保持する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#入力確認完了画面間で入力情報を保持する) (s9)
- [セッションストアの特長と選択基準](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアの特長と選択基準) (s16)
- [セッションストアを使用するための設定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#セッションストアを使用するための設定) (s8)
- [HIDDENストアの暗号化設定をカスタマイズする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md#hiddenストアの暗号化設定をカスタマイズする) (s12)
- [入力画面の初期表示](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#入力画面の初期表示) (s1)
- [入力画面から確認画面へ遷移](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#入力画面から確認画面へ遷移) (s2)
- [確認画面から入力画面へ戻る](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md#確認画面から入力画面へ戻る) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The actual output fully covers the key fact from the expected output: when multiple tab operations are not allowed, use DB store; when allowed, use HIDDEN store. This core information is clearly presented in both the conclusion and the table. The actual output goes significantly beyond the expected output with additional details, but the essential fact is explicitly covered. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the actual output is fully relevant to the input, which asks about how to differentiate between DB store and HIDDEN store when maintaining session variables across input, confirmation, and completion screens. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「複数タブ操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使う」は回答の結論「複数タブでの画面操作を許容しない場合は DBストア、複数タブを許容する場合は HIDDENストア を使用します」および表に明示されている |
| answer_relevancy | OK | 回答は質問（DBストアとHIDDENストアの使い分け）に直接答えており、選択基準・各ストアの特長・JSP実装例・Java実装例・注意点すべてが質問に関連した内容で構成されている。的外れな情報は含まれていない。 |
| faithfulness | OK | 回答の全内容がナレッジ（libraries-session-store.md）と一致している。使い分け基準（複数タブ許容しない→DBストア、許容する→HIDDENストア）、各ストアの特長、JSP実装コード、注意点（FormではなくEntityを格納、AES暗号化、冗長化時のキー設定、USER_SESSIONテーブル作成と期限切れセッション削除）のすべてがナレッジの記述と矛盾しない。 |

### 参照事実（expected_facts）

- 複数タブ操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使う
