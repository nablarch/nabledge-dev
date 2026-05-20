**結論**: 複数タブでの画面操作を**許容しない**場合はDBストアを、**許容する**場合はHIDDENストアを使用する。これが使い分けの唯一の判断基準です。

**根拠**:

セッションストアの特長と選択基準に明示されている通りです。

| 用途 | セッションストア |
|------|-----------------|
| 入力〜確認〜完了画面間で入力情報の保持（複数タブ操作を**許容しない**） | **DBストア** |
| 入力〜確認〜完了画面間で入力情報の保持（複数タブ操作を**許容する**） | **HIDDENストア** |

**DBストアの特長:**
- ローリングメンテナンス等でAPサーバが停止してもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合は後勝ち（先に保存されたデータは消失）

**HIDDENストアの特長:**
- クライアントサイドに `hidden` タグを使用してセッション変数を引き回して実現
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 複数スレッドで実行された場合、セッションデータはそれぞれのスレッドに紐付けて保存される

**HIDDENストアを使う場合のJSP実装例:**

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

**アクション実装例（入力→確認画面遷移、DBストア/HIDDENストア共通）:**

```java
// 入力画面から確認画面へ遷移
ProjectForm form = context.getRequestScopedVar("form");
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存（FormではなくEntityを格納すること）
SessionUtil.put(ctx, "project", project);
```

```java
// 登録処理を実行（完了画面）
Project project = SessionUtil.get(ctx, "project");
// 登録処理は省略
SessionUtil.delete(ctx, "project");
```

**注意点**:
- セッションストアにはFormではなくEntityを格納すること。Formを格納するとバリデーション前の信頼できない値を保持する可能性があり、セキュリティリスクが高まる。
- HIDDENストアを使用した場合、アプリケーションサーバが冗長化されているときは暗号化キーを明示的に設定する必要がある（デフォルトはAPサーバごとに異なるキーを自動生成するため、復号に失敗するケースがある）。
- DBストアを使用した場合、ブラウザを閉じた際などにテーブル上にセッション情報が残ることがあるため、期限切れのセッション情報は定期的に削除する必要がある。

参照: `component/libraries/libraries-session-store.json:s9`, `component/libraries/libraries-session-store.json:s16`, `component/libraries/libraries-create-example.json:s2`, `component/libraries/libraries-create-example.json:s4`