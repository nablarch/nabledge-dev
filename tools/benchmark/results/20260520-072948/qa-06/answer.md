**結論**: Nablarchのカスタムタグを使用することで、入力画面JSPをそのまま確認画面として流用できます。確認画面JSPには `n:confirmationPage` タグでパスを指定するだけで共通化が実現できます。

**根拠**:

入力画面と確認画面の共通化には以下の4つのカスタムタグを使用します。

| タグ | 用途 |
|------|------|
| `n:confirmationPage` | 確認画面JSPで入力画面のパスを指定（共通化の本体） |
| `n:forInputPage` | 入力画面でのみ表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面でのみ表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面で確認画面向け表示を無効化したい部分に指定 |

**入力画面のJSP**（ボタン部分だけ差分を記述）:

```jsp
<n:form>
  <!-- 入力欄は入力・確認画面で同じ記述を使用 -->
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
  <!-- ボタンだけforInputPage/forConfirmationPageで分岐 -->
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

**確認画面のJSP**（これだけでOK）:

```jsp
<!-- 入力画面のJSPへのパスを指定する -->
<n:confirmationPage path="./input.jsp" />
```

入力項目のカスタムタグ（`n:text`、`n:checkbox`、`n:select` など）は、入力画面と全く同じJSP記述のまま確認画面用の出力（テキスト表示）に切り替わります。

カスタムタグを使用するには、JSPに以下のtaglibディレクティブが必要です:

```jsp
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
```

**注意点**:
- `plainHidden` タグと `hiddenStore` タグは入力・確認画面ともに出力される（画面間のデータ受け渡し用のため）
- `ignoreConfirmation` タグは、チェックボックスのように確認画面でもチェック欄を表示したい場合など、確認画面向けの変換を無効化したい箇所に使用する
- カスタムタグを動作させるには `NablarchカスタムタグHTMLハンドラ` のハンドラ設定が必須

参照: libraries-tag.json:s23, libraries-tag.json:s3, libraries-tag-reference.json:s64, libraries-tag-reference.json:s66, libraries-tag-reference.json:s67, libraries-tag.json:s7