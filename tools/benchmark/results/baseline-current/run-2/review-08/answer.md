**結論**: 「複数タブでの画面操作を許容するか」が唯一の選択基準です。許容しない場合は **DBストア**、許容する場合は **HIDDENストア** を使います。

**根拠**:

| 用途 | 選択するストア |
|------|--------------|
| 入力〜確認〜完了画面間で保持（**複数タブ不許容**） | DBストア |
| 入力〜確認〜完了画面間で保持（**複数タブ許容**） | HIDDENストア |

**DBストアの特徴**
- データはデータベース上のテーブルに保存される
- ローリングメンテナンスでAPサーバが停止してもセッション変数を復元できる
- APサーバのヒープ領域を圧迫しない
- 同一セッションで複数スレッドが並行実行された場合は**後勝ち**（先のデータは消失）

**HIDDENストアの特徴**
- クライアントサイドに `hidden` タグで画面間を引き回す形で保存される
- 複数タブでの操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 複数スレッドが並行実行された場合、セッションデータはそれぞれのスレッドに紐付けて保存される

**HIDDENストア使用時のJSP設定**
```jsp
<n:form>
  <!-- name属性にはHiddenStoreのparameterNameプロパティの値を設定 -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

**セッションストアへの保存実装例（登録機能）**
```java
// リクエストスコープから入力情報を取得
ProjectForm form = context.getRequestScopedVar("form");

// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

**注意点**:
- セッションストアには **Form ではなく Entity（業務ロジック用オブジェクト）を格納する**こと。Formを格納するとバリデーション前の信頼できない値を保持するリスクがあり、業務ロジックに不要なデータ変換処理が混入する
- 認証情報の保持には DBストア または HTTPセッションストアが適切（HIDDENストアではない）
- 検索条件・検索結果一覧・セレクトボックス等の画面表示項目・エラーメッセージはセッションストアに保存しない

参照: `component/libraries/libraries-session-store.json#s9`, `component/libraries/libraries-session-store.json#s16`