**結論**: NablarchのJakarta Server Pagesカスタムタグが提供する `confirmationPage`タグ・`forInputPage`タグ・`forConfirmationPage`タグを使用することで、入力画面と確認画面のJSPを共通化できる。入力画面用に作成したJSPに、ボタンなどの差分のみを追加実装するだけで確認画面を実現できる。

**根拠**:

入力画面と確認画面の共通化には以下の4つのカスタムタグを使用する。

| タグ | 役割 |
|------|------|
| `confirmationPage` | 確認画面のJSPで入力画面のJSPパスを指定する |
| `forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `ignoreConfirmation` | 確認画面で確認画面向けの表示を無効化したい部分に指定する（例: 確認画面でもチェック欄を表示したい場合） |

**入力画面のJSP（input.jsp）**:

```jsp
<n:form>
  <!--
    入力欄は、入力画面と確認画面で同じJSP記述を使用する。
  -->
  <div>
    <label>名前</label>
    <n:text name="form.name" />
  </div>
  <div>
    <label>メール</label>
    <n:checkbox name="form.useMail" label="使用する" offLabel="使用しない" />
  </div>
  <div>
    <label>プラン</label>
    <n:select name="form.plan"
              listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
  </div>
  <!--
   ボタン表示は、入力画面と確認画面で異なるので、
   forInputPageタグとforConfirmationPageタグを使用する。
  -->
  <div style="padding: 8px 0;">
    <n:forInputPage>
      <n:submit type="submit" uri="/action/sample/confirm" value="確認" />
    </n:forInputPage>
    <n:forConfirmationPage>
      <n:submit type="submit" uri="/action/sample/showNew" value="戻る" />
      <n:submit type="submit" uri="/action/sample/register" value="登録" />
    </n:forConfirmationPage>
  </div>
</n:form>
```

**確認画面のJSP（confirm.jsp）**:

```jsp
<!--
  入力画面のJSPへのパスを指定する。
-->
<n:confirmationPage path="./input.jsp" />
```

確認画面のJSPはこれだけでよい。`confirmationPage`タグが入力画面のJSPをインクルードし、カスタムタグが自動的に入力欄を読み取り専用の表示に切り替える。

なお、入力画面から確認画面へ遷移する際は、入力情報をセッションストアに保存するのが標準的な実装パターンである：

```java
// リクエストスコープから入力情報を取得
ProjectForm form = context.getRequestScopedVar("form");

// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

確認画面から入力画面へ戻る際：

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
- `plainHidden`タグと`hiddenStore`タグは、画面遷移の状態受け渡し用として共通化の対象外となり、入力・確認画面ともに出力される
- カスタムタグを使用するには `nablarch-fw-web-tag` モジュールの依存関係と、Nablarchカスタムタグ制御ハンドラの設定が必要

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67, libraries-create-example.json:s2, libraries-create-example.json:s3

---