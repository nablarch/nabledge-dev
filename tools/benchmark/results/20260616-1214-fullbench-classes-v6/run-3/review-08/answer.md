**結論**: 「複数タブでの画面操作を許容するか否か」で使い分けます。許容しない場合はDBストア、許容する場合はHIDDENストアを使用します。

**根拠**:

| 要件 | 選択するストア |
|------|--------------|
| 入力～確認～完了画面間（複数タブ不許容） | DBストア |
| 入力～確認～完了画面間（複数タブ許容） | HIDDENストア |

**DBストアの特徴（複数タブ不許容の場合）**:
- セッション変数をデータベース上のテーブルに保存する
- アプリケーションサーバが停止してもセッションの復元が可能
- 同一セッションが複数スレッドで処理された場合は後勝ち（先のデータは消失）

**HIDDENストアの特徴（複数タブ許容の場合）**:
- クライアントサイドで hidden タグを使って画面間でセッション変数を引き回す
- 複数タブでの画面操作を許容できる
- 同一セッションが複数スレッドで処理された場合も、各スレッドに紐付けて保存される

HIDDENストアを使用する場合、入力・確認画面のJSPに `hiddenStore` タグを追加します：

```jsp
<n:form>
  <!--
    name属性にはHiddenStoreのparameterNameプロパティの値を設定
  -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

**アクション側の実装（いずれのストアでも共通）**:

```java
// 入力画面→確認画面：入力情報をセッションストアに保存
ProjectForm form = context.getRequestScopedVar("form");
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 完了処理：セッションストアからデータを取得して登録
Project project = SessionUtil.get(ctx, "project");
// 登録処理は省略
SessionUtil.delete(ctx, "project");
```

**注意点**: セッションストアに保存するのは Form ではなく、業務ロジック用の Entity（登録・更新対象オブジェクト）にすることが推奨されています。Form を格納すると業務ロジックに不要な変換処理が入り込み、セキュリティ上もバリデーション前の信頼できない値をセッションに保持するリスクがあります。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-create-example.json:s2, libraries-create-example.json:s4