**結論**: `confirmationPage`タグを使用すると、確認画面のJSPに入力画面JSPへのパスを指定するだけで共通化でき、入力画面向けJSPに差分（ボタン等）のみ追加するだけで確認画面を実現できます。

**根拠**:

Nablarchのカスタムタグには入力・確認画面のJSP共通化機能が含まれており、以下の4つのタグを組み合わせて使います。

| タグ | 役割 |
|---|---|
| `n:confirmationPage` | 確認画面JSPで入力画面JSPへのパスを指定（共通化の起点） |
| `n:forInputPage` | 入力画面のみに表示したい部分を囲む |
| `n:forConfirmationPage` | 確認画面のみに表示したい部分を囲む |
| `n:ignoreConfirmation` | 確認画面で確認画面向けの表示を無効化したい部分に指定 |

**入力画面のJSP（例）**:

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
  <!-- ボタンは画面によって異なるので forInputPage/forConfirmationPage で切り替え -->
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

**確認画面のJSP（これだけでOK）**:

```jsp
<!-- 入力画面のJSPへのパスを指定する -->
<n:confirmationPage path="./input.jsp" />
```

確認画面のJSPは上記1行のみ。入力系のカスタムタグが自動的に確認画面向けの表示（読み取り専用）に切り替わります。

**注意点**:
- カスタムタグを使用するには `Nablarchカスタムタグ制御ハンドラ` の設定が必須です（ハンドラキューに設定）。また `CustomTagConfig` をコンポーネント定義に `customTagConfig` という名前で追加することでタグのデフォルト値を設定できます。
- `plainHidden`タグと`hiddenStore`タグは例外で、入力・確認画面ともに出力されます。
- 入力～確認～完了画面間でデータを保持する場合は、セッションストアを併用します（複数タブ非許容→DBストア、複数タブ許容→HIDDENストア＋`hiddenStore`タグ）。セッションストアにはFormではなくEntityを格納することが推奨されています。

参照: `libraries-tag.json:s3`, `libraries-tag.json:s23`, `libraries-tag.json:s6`, `libraries-tag-reference.json:s64`, `libraries-tag-reference.json:s66`, `libraries-tag-reference.json:s67`, `libraries-tag-reference.json:s65`, `libraries-session-store.json:s9`

---