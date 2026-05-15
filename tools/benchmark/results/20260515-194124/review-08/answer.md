**結論**: 複数タブ操作を許容しない場合は **DBストア**、複数タブ操作を許容する場合は **HIDDENストア** を使用します。

---

**根拠**:

### 使い分けの基準

| 用途 | 使用するストア |
|---|---|
| 入力〜確認〜完了画面間（**複数タブ操作を許容しない**） | **DBストア** |
| 入力〜確認〜完了画面間（**複数タブ操作を許容する**） | **HIDDENストア** |

### DBストアの特徴
- セッション変数をデータベース上のテーブル（`USER_SESSION`）に保存
- ローリングメンテナンス等でAPサーバが停止してもセッション変数を復元できる
- 同一セッションが複数スレッドで処理された場合は**後勝ち**（先のデータが消失する）

### HIDDENストアの特徴
- セッション変数をクライアントサイドの hidden タグで画面間に引き回す
- **複数タブでの操作を許容**できる（タブごとにセッションデータが独立）
- JSP の入力・確認画面に `<n:hiddenStore>` タグが必要

```jsp
<n:form>
  <%-- name属性にはHiddenStoreのparameterNameプロパティの値を設定 --%>
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

### 実装例（SessionUtil の使い方）

**入力画面 → 確認画面へ遷移時（保存）**
```java
// FormからEntityへ変換してセッションストアに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);
```

**確認画面 → 入力画面へ戻る時（取得・削除）**
```java
Project project = SessionUtil.get(ctx, "project");
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);
context.setRequestScopedVar("form", form);
SessionUtil.delete(ctx, "project");
```

**登録処理時（取得・削除）**
```java
Project project = SessionUtil.get(ctx, "project");
// 登録処理...
SessionUtil.delete(ctx, "project");
```

---

**注意点**:

1. **セッションストアには Form ではなく Entity を格納すること。** Form を格納すると密結合なコードが生まれやすく、セキュリティ上のリスクも高まる。

2. **HIDDENストアのハンドラ配置制約**:
   - `SessionStoreHandler` は `HttpResponseHandler` より**後ろ**に配置する
   - HIDDENストア使用時は `MultipartRequestHandler` より**後ろ**に配置する
   - `SessionStoreHandler` は `InternalForwardHandler` より**前**に配置する（内部フォワード時に最新のセッション変数を取得できなくなるため）

3. **HIDDENストアと冗長化**: APサーバが冗長化されている場合、暗号化キーを明示的に設定する必要がある（デフォルトはサーバごとに異なるキーが自動生成されるため復号失敗の恐れあり）。

4. **DBストアの期限切れデータ**: ブラウザが閉じられた場合などにテーブル上にセッション情報が残ることがある。期限切れのセッション情報は定期的に削除する運用が必要。

5. **検索条件・エラーメッセージ等はセッションストアに保持しないこと**（選択基準上「使用しない」が推奨）。

参照: `component/libraries/libraries-session-store.json#s9`, `component/libraries/libraries-session-store.json#s16`, `component/libraries/libraries-session-store.json#s8`, `component/libraries/libraries-session-store.json#s12`, `component/handlers/handlers-SessionStoreHandler.json#s3`, `component/handlers/handlers-SessionStoreHandler.json#s4`, `component/libraries/libraries-create-example.json#s2`, `component/libraries/libraries-create-example.json#s3`, `component/libraries/libraries-create-example.json#s4`