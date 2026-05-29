Step 5-7: 回答を生成し、検証します。

**結論**: `n:confirmationPage` タグを使うことで、入力画面のJSPをそのまま確認画面に流用できます。確認画面のJSPは `<n:confirmationPage path="./input.jsp" />` の1行だけで、入力欄の表示切り替えはカスタムタグ側が自動処理します。

**根拠**:

確認画面JSP（これだけでよい）:
```jsp
<!--
  入力画面のJSPへのパスを指定する。
-->
<n:confirmationPage path="./input.jsp" />
```

入力画面JSP（ボタン部分のみ分岐を追加）:
```jsp
<n:form>
  <!-- 入力欄はそのまま — 確認画面でも同じ記述で表示される -->
  <div>
    <label>名前</label>
    <n:text name="form.name" />
  </div>
  <div>
    <label>プラン</label>
    <n:select name="form.plan"
              listName="plans"
              elementLabelProperty="planName"
              elementValueProperty="planId" />
  </div>
  <!-- ボタンなど差分がある部分だけ分岐 -->
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

使用するタグ:

| タグ | 役割 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPへのパスを指定。入力系タグを自動的に確認画面向け出力に切り替える |
| `n:forInputPage` | 囲んだ範囲を入力画面でのみ表示 |
| `n:forConfirmationPage` | 囲んだ範囲を確認画面でのみ表示 |
| `n:ignoreConfirmation` | 確認画面向けの自動変換を無効化（例：確認画面でもチェックボックスのUI表示を維持したい場合） |

入力情報の画面間保持（セッションストア）:

```java
// 入力画面 → 確認画面: FormをEntityに変換してセッションに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認画面 → 入力画面（戻る）: セッションから取り出してFormに変換
Project project = SessionUtil.get(ctx, "project");
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);
context.setRequestScopedVar("form", form);
SessionUtil.delete(ctx, "project");
```

**注意点**:
- `n:plainHidden`・`n:hiddenStore` タグは入力/確認画面ともに出力されます（画面間のデータ受け渡し用のため、共通化の対象外）
- セッションストアには Form ではなく Entity を格納してください。Form を格納するとバリデーション前の信頼できない値がセッションに残るリスクがあります
- 複数タブ操作を許容する場合は HIDDENストア（`n:hiddenStore` タグ）、許容しない場合は DBストアを使い分けます

参照: libraries-tag.json:s3, libraries-tag.json:s23, libraries-tag-reference.json:s64, libraries-tag-reference.json:s65, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67, libraries-session-store.json:s9, libraries-create-example.json:s2, libraries-create-example.json:s3

---