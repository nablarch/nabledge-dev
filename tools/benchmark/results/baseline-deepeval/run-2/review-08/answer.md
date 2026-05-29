Step 5: セクション内容を基に回答を生成します。

---

**結論**: 複数タブでの画面操作を許容しない場合は **DBストア**、許容する場合は **HIDDENストア** を使用します。

---

**根拠**:

### 使い分けの判断基準

| 用途 | ストア |
|---|---|
| 入力～確認～完了画面間の入力情報保持（複数タブ **不許可**） | DBストア |
| 入力～確認～完了画面間の入力情報保持（複数タブ **許可**） | HIDDENストア |

### 各ストアの仕組みと特長

**DBストア**
- セッション変数をデータベースのテーブル（`USER_SESSION`）に保存する
- 同一セッションで複数スレッドが同時実行された場合、**後勝ち**になる（先に保存されたデータは消失）
- アプリケーションサーバが停止してもセッション変数を復元できる

**HIDDENストア**
- `<n:hiddenStore>` タグを使い、セッション変数を画面の hidden フィールドとしてクライアントサイドに保持し、画面間で引き回す
- 同一セッションで複数スレッドが実行された場合でも、**各スレッドにそれぞれ紐付けて保存**されるため複数タブが共存できる
- JSPの各フォームに `<n:hiddenStore>` タグが必要:

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

### 実装パターン（DBストア・HIDDENストア共通）

セッションストアの操作は `SessionUtil` を使い、**Formではなく Entity を格納**する。

```java
// 入力画面の初期表示: 残存セッションをクリア
SessionUtil.delete(ctx, "project");

// 入力→確認 遷移時: FormをEntityへ変換してセッションに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認→入力 戻り時: セッションから取得・削除し、Formに戻す
Project project = SessionUtil.get(ctx, "project");
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);
context.setRequestScopedVar("form", form);
SessionUtil.delete(ctx, "project");

// 完了処理: セッションから取得・登録後に削除
Project project = SessionUtil.get(ctx, "project");
// ... 登録処理 ...
SessionUtil.delete(ctx, "project");
```

> Entityを格納する理由: Formはバリデーション前の信頼できない値を含む可能性があるため、セキュリティと凝集性の観点からEntityに変換してから保存する。

---

**注意点**:

- **DBストアの後勝ち**: 同一セッションで複数スレッドが同時実行されると先のデータが消失する。複数タブ操作を許容したい場合は必ずHIDDENストアを選ぶこと
- **HIDDENストアの冗長化**: アプリケーションサーバが冗長化されている場合、サーバごとに異なる暗号化キーが生成されるため、復号に失敗することがある。この場合は暗号化キー（AES）を明示的に設定する
- **HIDDENストアのハンドラ配置制約**: セッション変数保存ハンドラは「マルチパートリクエストハンドラ **より後ろ**」かつ「内部フォーワードハンドラ **より前**」に配置すること（内部フォワード時に最新のセッション変数を取得するため）
- **DBストアの期限切れデータ**: ブラウザが直接閉じられた場合などに `USER_SESSION` テーブルにデータが残るため、期限切れセッションを定期的に削除する仕組みが必要

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-create-example.json:s1, libraries-create-example.json:s2, libraries-create-example.json:s3, libraries-create-example.json:s4, libraries-session-store.json:s12, handlers-SessionStoreHandler.json:s3

---