**結論**: 複数タブでの画面操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使います。

**根拠**:

Nablarchのセッションストアでは、入力〜確認〜完了画面間の用途に応じて2種類のストアを使い分けます。

| 用途 | セッションストア |
|---|---|
| 入力～確認～完了画面間の保持（複数タブ不許容） | DBストア |
| 入力～確認～完了画面間の保持（複数タブ許容） | HIDDENストア |

**DBストアの特徴**（データベース上のテーブルに保存）:
- ローリングメンテナンス等でAPサーバが停止してもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合は後勝ち（先に保存されたデータは消失する）

**HIDDENストアの特徴**（hiddenタグを使ってクライアントサイドに保持）:
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 複数スレッドで実行された場合、各スレッドに紐付けて保存される

HIDDENストアを使う場合、入力画面・確認画面のJSPに `hiddenStore` タグを追加します:

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

いずれのストアを使う場合も、`SessionUtil` を使って読み書きする実装パターンは共通です:

```java
// 入力→確認画面への遷移時
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);  // ストア名を省略するとデフォルトストアへ保存

// 確認→完了（登録処理）
Project project = SessionUtil.get(ctx, "project");
// 登録処理...
SessionUtil.delete(ctx, "project");  // 完了後は削除
```

**注意点**:
- セッションストアに保存するのはFormではなくEntity（業務ロジック用オブジェクト）にすること。Formを格納するとバリデーション前の信頼できない値をセッションに保持するリスクがある
- DBストアを使用する場合、ブラウザを閉じたときにテーブル上にセッション情報が残ることがあるため、期限切れのセッション情報を定期削除する仕組みが必要
- HIDDENストアはAPサーバが冗長化されている場合、暗号化キーをサーバ間で統一しないと復号失敗が起きる可能性がある

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-create-example.json:s2, libraries-create-example.json:s4