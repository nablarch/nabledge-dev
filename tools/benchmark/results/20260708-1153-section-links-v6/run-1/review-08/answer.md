**結論**: 入力→確認→完了画面間のセッション変数保持において、**複数タブでの操作を許容しない**ならDBストア、**複数タブを許容する**ならHIDDENストアを使用します。

**根拠**:

| 用途 | セッションストア |
|---|---|
| 複数タブでの画面操作を許容しない | DBストア（データベース上のテーブルに保存） |
| 複数タブでの画面操作を許容する | HIDDENストア（クライアントサイドでhiddenタグを使って引き回す） |

**DBストアの特徴**
- サーバ停止時でもセッション変数の復元が可能
- 同一セッションで複数スレッドが動いた場合、後勝ち（先のデータが消失する）

**HIDDENストアの特徴**
- 複数タブでの操作を許容できる
- 各スレッドに紐付けてデータを保存するため、複数タブが独立して動作する
- JSP側で `<n:hiddenStore>` タグを追加する必要がある

```jsp
<n:form>
  <!-- name属性にはHiddenStoreのparameterNameプロパティの値を設定 -->
  <n:hiddenStore name="nablarch_hiddenStore" />
</n:form>
```

**SessionUtilによる実装例（入力→確認→完了）**

```java
// 入力画面の初期表示時：セッションが残っている場合は削除
SessionUtil.delete(ctx, "project");

// 確認画面遷移時：FormをEntityに変換してセッションストアに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認→入力に戻る場合：セッションから取得し削除
Project project = SessionUtil.get(ctx, "project");
SessionUtil.delete(ctx, "project");

// 完了処理：セッションから取得して登録後に削除
Project project = SessionUtil.get(ctx, "project");
// 登録処理...
SessionUtil.delete(ctx, "project");
```

**注意点**:
- セッションストアには **Formではなく Entity** を格納すること。Formを格納すると不要な変換処理が混入し密結合になるほか、信頼できない値をセッションに保持するセキュリティリスクがある。
- DBストアを使用する場合は `USER_SESSION` テーブルの作成が必要で、期限切れのセッション情報を定期削除する運用が必要。

参照:
- セッションストア
  .claude/skills/nabledge-6/docs/component/libraries/libraries-session-store.md
  入力～確認～完了画面間で入力情報を保持する
  セッションストアの特長と選択基準
- 登録機能での実装例
  .claude/skills/nabledge-6/docs/component/libraries/libraries-create-example.md
  入力画面の初期表示
  入力画面から確認画面へ遷移
  確認画面から入力画面へ戻る
  登録処理を実行