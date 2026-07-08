**結論**: Nablarchのカスタムタグ機能を使うと、確認画面のJSPを `<n:confirmationPage>` タグ1行に削減できます。入力画面のJSPはほぼそのまま流用し、ボタンなど入力/確認で異なる部分だけ `<n:forInputPage>` / `<n:forConfirmationPage>` で出し分けます。

**根拠**:

入力項目のカスタムタグ（`n:text`、`n:select`、`n:checkbox` など）は、入力画面と全く同じJSP記述のまま確認画面用の表示（ラベル形式）に自動変換できます。

**確認画面のJSP（ほぼ1行で完成）**:

```jsp
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
<!-- 登録画面を確認画面に変換して表示する -->
<n:confirmationPage path="./create.jsp" ></n:confirmationPage>
```

`<n:confirmationPage path="...">` に入力画面JSPへのパスを指定するだけで、入力画面のJSPが確認画面向けに変換されて表示されます。

**入力画面側のJSP（ボタンの出し分けのみ追加）**:

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

使用するタグのまとめ:

| タグ | 役割 |
|---|---|
| `<n:confirmationPage path="...">` | 確認画面のJSPで入力画面JSPのパスを指定する |
| `<n:forInputPage>` | 入力画面でのみ表示したい部分を囲む |
| `<n:forConfirmationPage>` | 確認画面でのみ表示したい部分を囲む |
| `<n:ignoreConfirmation>` | 確認画面での確認画面向け変換を無効化したい部分に指定（例: チェック欄をそのまま表示したい場合） |

**注意点**: `plainHidden`タグと `hiddenStore`タグは例外で、入力・確認画面ともに出力されます（画面間のデータ受け渡し用途のため）。

参照:
- Jakarta Server Pagesカスタムタグ
  .claude/skills/nabledge-6/docs/component/libraries/libraries-tag.md
  入力画面と確認画面のJSPを共通化して実装を減らす
  入力画面と確認画面を共通化する
- 登録内容の確認
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-client-create2.md
  登録内容の確認