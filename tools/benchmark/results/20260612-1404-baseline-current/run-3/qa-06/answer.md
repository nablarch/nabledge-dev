**結論**: `confirmationPageタグ`を使えば、確認画面のJSPに入力画面JSPへのパスを1行指定するだけで共通化できます。入力画面のJSPをそのまま流用し、差分（ボタン表示の切り替えなど）は`forInputPageタグ`／`forConfirmationPageタグ`で制御します。

---

**根拠**:

**使用するカスタムタグ**

| タグ | 用途 |
|------|------|
| `<n:confirmationPage path="..." />` | 確認画面JSPに記述。`path`属性で入力画面JSPのパスを指定する |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面で確認画面向け表示を無効化したい部分に指定（例: チェックボックスをそのまま表示したい場合）|

**入力画面のJSP（input.jsp）**

```jsp
<n:form>
  <!-- 入力欄は入力画面・確認画面で共通のJSP記述を使用 -->
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
  <!-- ボタン表示のみ入力画面・確認画面で切り替える -->
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

**確認画面のJSP（confirm.jsp）**

```jsp
<!-- 入力画面JSPへのパスを1行指定するだけ -->
<n:confirmationPage path="./input.jsp" />
```

**アクション側の実装（入力→確認への遷移）**

```java
// リクエストスコープから入力情報を取得
ProjectForm form = context.getRequestScopedVar("form");
// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);
// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

**アクション側の実装（確認→入力へ戻る）**

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

---

**注意点**:
- Nablarchカスタムタグを使用する場合は「Nablarchカスタムタグ制御ハンドラ」の設定が必須です。
- `<n:plainHidden>`タグおよび`<n:hiddenStore>`タグは、入力画面・確認画面の両方で出力されます（画面間のデータ受け渡し用途のため）。
- 入力欄以外のタグ（通常のHTMLタグなど）は確認画面でもそのまま出力されるため、表示を切り替えたい箇所のみ`forInputPage`/`forConfirmationPage`で囲んでください。

参照: `libraries-tag.json:s3`, `libraries-tag.json:s23`, `libraries-tag-reference.json:s64`, `libraries-tag-reference.json:s65`, `libraries-tag-reference.json:s66`, `libraries-tag-reference.json:s67`, `libraries-create-example.json:s2`, `libraries-create-example.json:s3`