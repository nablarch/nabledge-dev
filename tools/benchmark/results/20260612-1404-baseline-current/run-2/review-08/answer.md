**結論**: 入力→確認→完了画面間のセッション変数保持では、**複数タブ操作を許容しない場合はDBストア**、**複数タブ操作を許容する場合はHIDDENストア**を使用します。

---

**根拠**:

**選択基準（s16）**

| 用途 | セッションストア |
|---|---|
| 入力～完了画面間の入力情報保持（複数タブ不許容） | **DBストア** |
| 入力～完了画面間の入力情報保持（複数タブ許容） | **HIDDENストア** |

**各ストアの特長（s16）**

| 観点 | DBストア | HIDDENストア |
|---|---|---|
| 保存先 | データベース上のテーブル | クライアントサイド（hiddenタグ） |
| APサーバ停止時の復元 | 可能 | 不可 |
| ヒープ圧迫 | なし | なし |
| 複数スレッド競合時 | 後勝ち（先の保存が消失） | スレッドごとに独立して保存 |

**HIDDENストア使用時のJSP実装（s9）**

HIDDENストアを使用する場合、入力・確認画面のJSPに `hiddenStore` タグを配置します。

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

**セッション変数の操作例（create-example s2/s3/s4）**

```java
// 入力画面→確認画面: Entityをセッションストアに保存
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 確認画面→入力画面（戻る）: セッションストアから取得して削除
Project project = SessionUtil.get(ctx, "project");
SessionUtil.delete(ctx, "project");

// 完了処理: セッションストアから取得して削除
Project project = SessionUtil.get(ctx, "project");
SessionUtil.delete(ctx, "project");
```

---

**注意点**:

1. **セッションストアにはFormではなくEntityを保存すること（s9）**: Formを保存するとバリデーション前の信頼できない値が生存期間の長いセッションに残るリスクがあります。

2. **DBストアはUSER_SESSIONテーブルの作成が必要（s8）**: `SESSION_ID`はCHARではなくVARCHARで定義してください（Oracleで正常動作しないケースがあるため）。また、ブラウザを閉じた際にテーブルにセッション情報が残る場合があるため、期限切れセッションの定期削除が必要です。

3. **HIDDENストアのハンドラ配置制約（s3）**: セッション変数保存ハンドラは、マルチパートリクエストハンドラより後ろ、かつ内部フォーワードハンドラより前に配置する必要があります。内部フォーワードハンドラの後に置くと、フォワード時に最新のセッション変数を取得できない問題が発生します。

4. **APサーバ冗長化環境でのHIDDENストア（s12）**: サーバごとに異なる暗号化キーが生成されると復号に失敗するため、キーを明示的に設定してください。

参照: `libraries-session-store.json:s16`, `libraries-session-store.json:s9`, `libraries-session-store.json:s8`, `libraries-session-store.json:s12`, `handlers-SessionStoreHandler.json:s3`, `libraries-create-example.json:s2`, `libraries-create-example.json:s3`, `libraries-create-example.json:s4`