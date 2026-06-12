**結論**: 入力→確認→完了画面間でのセッション変数保持は、**複数タブでの画面操作を許容しない場合はDBストア**、**許容する場合はHIDDENストア**を使用します。

---

**根拠**:

| 観点 | DBストア | HIDDENストア |
|------|----------|--------------|
| 保存先 | データベース上のテーブル | クライアントサイド（hidden タグで画面間を引き回す） |
| 複数タブ対応 | 不可（同一セッションの後勝ちでデータ消失） | 可能（各タブ独立してデータ保持） |
| APサーバ停止時 | セッション変数の復元が可能 | 復元不可（クライアントが保持） |
| ヒープ圧迫 | なし | なし |
| 複数スレッド同時実行時 | 後勝ち（先に保存されたデータが消失） | 各スレッドに紐付けて個別保存 |

**HIDDENストア使用時のJSP設定**（入力・確認画面のJSPに必須）:

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

**セッション変数の操作（SessionUtil）**:

```java
// 入力→確認画面遷移時: FormからEntityへ変換してセッションストアに保存
ProjectForm form = context.getRequestScopedVar("form");
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 完了処理時: セッションストアから取得して削除
Project project = SessionUtil.get(ctx, "project");
// 登録処理は省略
SessionUtil.delete(ctx, "project");
```

---

**注意点**:

1. **セッションストアにはFormではなくEntityを格納すること。** Formを格納するとバリデーション前の信頼できない値が長期保持されるリスクがあり、セキュリティ上好ましくない。また業務ロジックへの不要な変換処理混入を防ぐ意味もある。

2. **HIDDENストア使用時のハンドラ配置制約**（`SessionStoreHandler`の位置）:
   - `マルチパートリクエストハンドラ`より**後ろ**に配置すること（リクエストパラメータへのアクセスに必要）
   - `内部フォーワードハンドラ`より**前**に配置すること（内部フォーワード時に最新のセッション変数を取得できなくなるため）

3. **DBストアのテーブル管理**: ブラウザが閉じられた場合などにテーブル上にセッション情報が残ることがある。期限切れのセッション情報は定期的に削除する必要がある。

参照: `libraries-session-store.json:s9`, `libraries-session-store.json:s16`, `handlers-SessionStoreHandler.json:s3`, `libraries-create-example.json:s2`, `libraries-create-example.json:s4`