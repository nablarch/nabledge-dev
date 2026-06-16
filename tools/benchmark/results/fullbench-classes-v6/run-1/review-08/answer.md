**結論**: 複数タブでの画面操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使用する。これが入力～確認～完了画面間でのセッション変数保持におけるストア選択の基準です。

**根拠**:

セッションストアの選択基準（`セッションストアの特長と選択基準` より）:

| 用途 | セッションストア |
|---|---|
| 入力～確認～完了画面間で入力情報の保持（**複数タブ不可**） | **DBストア** |
| 入力～確認～完了画面間で入力情報の保持（**複数タブ許容**） | **HIDDENストア** |

各ストアの特長:

**DBストア**（データベース上のテーブルに保存）
- ローリングメンテナンス等でAPサーバが停止してもセッション変数の復元が可能
- APサーバのヒープを圧迫しない
- 同一セッションが複数スレッドで実行された場合は**後勝ち**（先に保存されたデータは消失）

**HIDDENストア**（クライアントサイドのhiddenタグで引き回す）
- **複数タブでの画面操作を許容できる**
- APサーバのヒープを圧迫しない
- 同一セッションの複数スレッド実行時、データはそれぞれのスレッドに紐付けて保存される

HIDDENストアを使用する場合は、入力・確認画面のJSPに `hiddenStore` タグが必要です:

```jsp
<n:form>
  <!--
    name属性にはコンポーネント設定ファイルで定義した
    HiddenStoreのparameterNameプロパティの値を設定
  -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

セッション変数の読み書きは `SessionUtil` を使います（実装例より）:

```java
// 入力→確認遷移時: FormからEntityへ変換してセッションに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認→戻る時: セッションから取り出してFormに戻す
Project project = SessionUtil.get(ctx, "project");
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);
SessionUtil.delete(ctx, "project");

// 登録処理時: セッションから取り出して業務ロジックに使用し、削除
Project project = SessionUtil.get(ctx, "project");
// 登録処理...
SessionUtil.delete(ctx, "project");
```

**注意点**:
- セッションストアにはFormではなくEntity（業務ロジック用オブジェクト）を格納すること。Formを格納すると不要な変換処理が業務ロジックに混入しやすくなり、セキュリティの観点からも信頼できない値を長期保持するリスクがある
- HIDDENストアはデータが暗号化されてクライアントに送信されるが、アプリケーションサーバが冗長化されている場合はサーバ間で共通の暗号化キーを明示的に設定する必要がある（デフォルトではサーバごとにキーが自動生成されるため）
- セッションを使用し始める際は、入力画面の初期表示時に `SessionUtil.delete(ctx, "project")` で以前のセッションを削除しておくこと（ブラウザを直接閉じた場合などに残存している可能性があるため）

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s2, libraries-session-store.json:s12, libraries-create-example.json:s1, libraries-create-example.json:s2, libraries-create-example.json:s3, libraries-create-example.json:s4