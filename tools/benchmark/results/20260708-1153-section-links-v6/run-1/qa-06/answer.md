**結論**: Nablarchのカスタムタグ機能（`confirmationPageタグ`、`forInputPageタグ`、`forConfirmationPageタグ`）を使用することで、入力画面と確認画面のJSPを共通化できます。確認画面JSPで入力画面のパスを指定するだけで、入力画面のJSPをそのまま確認画面に流用できます。

**根拠**:

**確認画面JSP側の記述**（`confirmationPageタグ`で入力画面のパスを指定）:
```jsp
<n:confirmationPage path="/WEB-INF/view/register/input.jsp" />
```

**入力画面JSP側の記述**（差分のみ追加）:
```jsp
<%-- 入力画面でのみ表示したい部分（例：「確認へ」ボタン） --%>
<n:forInputPage>
  <n:submit value="確認" uri="/confirm" />
</n:forInputPage>

<%-- 確認画面でのみ表示したい部分（例：「登録」ボタン） --%>
<n:forConfirmationPage>
  <n:submit value="登録" uri="/register" />
</n:forConfirmationPage>
```

`ignoreConfirmationタグ` は、確認画面での確認向け表示を無効化したい部分に使用します（例：チェックボックスを確認画面でもチェック欄のまま表示したい場合）。

**画面間の入力データ保持**には `SessionUtil` を使用します:

```java
// 入力→確認画面遷移時：FormからEntityへ変換してセッションに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認→入力画面へ戻る時
Project project = SessionUtil.get(ctx, "project");
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);
context.setRequestScopedVar("form", form);
SessionUtil.delete(ctx, "project");

// 登録処理実行時
Project project = SessionUtil.get(ctx, "project");
// 登録処理...
SessionUtil.delete(ctx, "project");
```

セッションストアの選択:
- **複数タブ操作を許容しない場合**: DBストアを使用
- **複数タブ操作を許容する場合**: HIDDENストアを使用（JSPに `hiddenStoreタグ` が必要）

**注意点**:
- 入力データ保持には、ウィンドウスコープ（hiddenタグによるクライアント保持）ではなくセッションストアを使用すること。ウィンドウスコープはBeanをそのまま格納できず実装が煩雑になる。
- セッションストアには、FormではなくEntityオブジェクトを格納すること。

参照:
- Jakarta Server Pagesカスタムタグ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md
  入力画面と確認画面のJSPを共通化して実装を減らす
  入力画面と確認画面を共通化する
- タグリファレンス
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag-reference.md
  confirmationPageタグ
  ignoreConfirmationタグ
  forInputPageタグ
  forConfirmationPageタグ
- セッションストア
  .claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md
  入力～確認～完了画面間で入力情報を保持する
- 登録機能での実装例
  .claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md
  入力画面から確認画面へ遷移
  確認画面から入力画面へ戻る
  登録処理を実行