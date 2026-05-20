**結論**: 複数タブ操作を**許容しない**場合はDBストア、**許容する**場合はHIDDENストアを使用する。

**根拠**:

公式の選択基準（s16）に基づくと以下の通り：

| 用途 | セッションストア |
|---|---|
| 入力～確認～完了画面間での入力情報保持（複数タブ不可） | DBストア |
| 入力～確認～完了画面間での入力情報保持（複数タブ許容） | HIDDENストア |

**DBストアの特徴**（s16）:
- 保存先: データベース上のテーブル
- ローリングメンテナンス等でAPサーバーが停止してもセッション変数の復元が可能
- 同一セッションを複数スレッドで処理した場合は**後勝ち**（先に保存されたデータは消失）

**HIDDENストアの特徴**（s16）:
- 保存先: クライアントサイド（`hidden` タグで画面間引き回し）
- 複数タブでの画面操作を許容できる
- 同一セッションを複数スレッドで処理した場合、データはそれぞれのスレッドに紐付けて保存される

**HIDDENストア使用時のJSP実装**（s9）:

入力・確認画面のJSPに `hiddenStore` タグを追加する必要がある：

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

**セッション変数の操作（登録機能の例）**（libraries-create-example）:

```java
// 入力画面から確認画面へ遷移時：FormをEntityに変換してputする
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);

// 登録処理実行時：getして使い、完了後にdeleteする
Project project = SessionUtil.get(ctx, "project");
// 登録処理は省略
SessionUtil.delete(ctx, "project");
```

**注意点**:

- **DBストアの後勝ち動作**: 同一セッションで複数スレッドが競合すると先に保存されたデータが消える。複数タブ操作を許容する要件では使用しないこと（s16）
- **HIDDENストアの冗長化対応**: APサーバーが冗長化されている場合、デフォルトの自動生成キーだとサーバーごとに異なるキーになり復号に失敗するケースがある。その場合は `AesEncryptor` で暗号化キーを明示的に設定する（s12）
- **格納対象はFormではなくEntity**: セキュリティとコードの凝集性の観点から、セッションストアにはFormではなく業務ロジック用のEntityを格納すること（s9）

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s12, libraries-create-example.json:s1, libraries-create-example.json:s2, libraries-create-example.json:s3, libraries-create-example.json:s4