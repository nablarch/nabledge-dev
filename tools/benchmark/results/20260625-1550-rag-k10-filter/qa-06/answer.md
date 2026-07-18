はい、Nablarchのカスタムタグを使って入力画面と確認画面のJSPを共通化できます。

## 概要

入力画面向けに作成したJSPに、確認画面との差分（ボタンなど）のみを追加するだけで確認画面を作成できます。

## 使用するカスタムタグ

| タグ | 役割 |
|------|------|
| `<n:confirmationPage>` | 確認画面のJSPで入力画面JSPへのパスを指定する |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面で確認画面向け表示を無効化したい部分に指定する（例：チェックボックスをそのまま表示したい場合） |

## 実装例

**入力画面 (input.jsp)**

```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じJSP記述を使用 -->
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
  <!-- ボタンは画面ごとに異なるので切り替える -->
  <div>
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

**確認画面 (confirm.jsp)**

```jsp
<!-- 入力画面のJSPへのパスを指定するだけ -->
<n:confirmationPage path="./input.jsp" />
```

## 注意事項

- `<n:plainHidden>` と `<n:hiddenStore>` は入力・確認画面の両方で出力されます（画面間のデータ受け渡し用途のため）
- 入力・確認画面の表示制御は**入力系タグが対象**です

## 画面間のデータ保持

入力→確認→完了の画面遷移でデータを保持するにはセッションストアを使います。

- **複数タブ不許容** → DBストアを使用
- **複数タブ許容** → HIDDENストアを使用し、JSPに `<n:hiddenStore>` タグを追加

セッションストアにはFormではなく**Entity**を格納することが推奨されています（業務ロジックの凝集性向上とセキュリティ上の理由から）。