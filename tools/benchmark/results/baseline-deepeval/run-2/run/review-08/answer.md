**結論**: 複数タブでの画面操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使用する。

**根拠**:

**選択基準**

| 用途 | ストア |
|------|--------|
| 入力～確認～完了画面間の保持（複数タブ不許容） | **DBストア** |
| 入力～確認～完了画面間の保持（複数タブ許容） | **HIDDENストア** |

各ストアの特長は以下の通り。

| 特長 | DBストア | HIDDENストア |
|------|----------|--------------|
| 保存先 | データベース上のテーブル | クライアントサイド（hiddenタグで画面間引き回し） |
| 複数タブ | 不可（後勝ちで先のデータ消失） | 可能（スレッドごとに独立保存） |
| APサーバ停止時 | セッション変数を復元可能 | 復元不可 |
| ヒープ影響 | なし | なし |

**HIDDENストアを使用する場合のJSP設定**

入力・確認画面のJSPに `hiddenStore` タグを追加する必要がある。

```jsp
<n:form>
  <!--
    name属性にはコンポーネント設定ファイルに定義した
    HiddenStoreのparameterNameプロパティの値を設定
  -->
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

**セッションストア操作の実装例（登録機能）**

入力→確認へ遷移時（保存）:
```java
// FormからEntityへ変換してセッションストアに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);
```

確認→入力へ戻る時（取得・削除）:
```java
Project project = SessionUtil.get(ctx, "project");
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);
context.setRequestScopedVar("form", form);
SessionUtil.delete(ctx, "project");
```

完了処理実行時（取得・削除）:
```java
Project project = SessionUtil.get(ctx, "project");
// 登録処理
SessionUtil.delete(ctx, "project");
```

**注意点**:

- **FormではなくEntityを格納すること**: Entityを格納することでセッションから取り出してすぐ業務ロジックを実行できる。Formを格納するとバリデーション前の信頼できない値が保持されるリスクがある。
- **HIDDENストアのハンドラ配置制約**: マルチパートリクエストハンドラより後ろ、かつ内部フォーワードハンドラより前に `SessionStoreHandler` を配置すること。内部フォーワードハンドラより後ろに置くと、内部フォワード時に最新のセッション変数を取得できない問題が発生する。
- **HIDDENストアの冗長化対応**: APサーバが冗長化されている場合、サーバごとに異なる暗号化キーが生成されて復号に失敗するケースがある。その場合は `HiddenStore` の `encryptor` プロパティで暗号化キーを明示的に設定すること。
- **DBストアのテーブル作成**: DBストアを使用する場合は `USER_SESSION` テーブル（`SESSION_ID`/`SESSION_OBJECT`/`EXPIRATION_DATETIME` カラム）を作成する必要がある。また、ブラウザが閉じられた際にテーブル上にセッション情報が残ることがあるため、期限切れのセッション情報を定期的に削除する設計が必要。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-create-example.json:s2, libraries-create-example.json:s3, libraries-create-example.json:s4, libraries-session-store.json:s12, handlers-SessionStoreHandler.json:s3, libraries-session-store.json:s8

---