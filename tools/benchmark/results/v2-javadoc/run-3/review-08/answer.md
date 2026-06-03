Step 4でread-sections.shを実行します（既にJSONを直接読み込んでいるのでその内容を使用）。

`read_sections`: `component/libraries/libraries-session-store.json:s9`, `component/libraries/libraries-session-store.json:s16`, `component/libraries/libraries-session-store.json:s2`, `component/libraries/libraries-session-store.json:s8`, `component/libraries/libraries-create-example.json:s2`, `component/libraries/libraries-create-example.json:s4`

Step 5〜7を経て、回答を出力します。

---

**結論**: 複数タブでの画面操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使用する。

**根拠**:

Nablarchのセッションストアは保存先と特性によって使い分ける。

| 用途 | セッションストア |
|---|---|
| 入力〜確認〜完了画面間の保持（複数タブ不許容） | DBストア |
| 入力〜確認〜完了画面間の保持（複数タブ許容） | HIDDENストア |

**DBストアの特長:**
- データベース上のテーブル（`USER_SESSION`）に保存
- ローリングメンテナンス等でサーバが停止しても復元可能
- アプリケーションサーバのヒープ領域を圧迫しない
- 同一セッションが複数スレッドで処理された場合は後勝ち（先に保存されたデータは消失）

**HIDDENストアの特長:**
- `hidden`タグで画面間引き回すクライアントサイド保存
- 複数タブでの画面操作を許容できる
- 各スレッドに紐付けてデータが保存されるため後勝ちは発生しない

**HIDDENストアを使用する場合、入力・確認画面のJSPに`n:hiddenStore`タグが必要:**

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

**どちらのストアも共通のAPIで操作する:**

```java
// 入力画面 → 確認画面へ遷移時: Entityをセッションストアに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認画面 → 登録処理: セッションストアから取得して処理
Project project = SessionUtil.get(ctx, "project");
// 登録処理は省略

// 登録後: セッションストアから削除
SessionUtil.delete(ctx, "project");
```

**注意点**:
- セッションストアにはFormではなくEntityを格納すること。FormはバリデーションAPI前だと信頼できない値を持ち、セキュリティリスクになるほか、業務ロジックに不要な変換処理が混入し密結合なソースになりやすい
- HIDDENストアをアプリケーションサーバが冗長化されている環境で使用する場合、サーバごとに異なる暗号化キーが生成されて復号に失敗するケースがある。この場合は`AesEncryptor`で暗号化キーを明示的に設定する
- DBストアを使用する場合は`USER_SESSION`テーブルの作成と、ブラウザが閉じられた際に残る期限切れセッション情報を定期削除する仕組みが必要

参照: `libraries-session-store.json:s9`, `libraries-session-store.json:s16`, `libraries-create-example.json:s2`, `libraries-create-example.json:s4`

---