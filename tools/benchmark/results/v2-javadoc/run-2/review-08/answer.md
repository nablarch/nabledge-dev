Step 5: 回答を生成します。

**検証 (Step 6):**

Nablarch固有のクレームを確認:
- 「複数タブを許容しない → DBストア」 → s9/s16で明記 ✓
- 「複数タブを許容する → HIDDENストア」 → s9/s16で明記 ✓
- 「HIDDENストアは`<n:hiddenStore>`タグが必要」 → s9で明記 ✓
- 「DBストアはサーバ停止後もセッション変数の復元が可能」 → s16で明記 ✓
- 「HIDDENストアはタブごとに独立したセッションデータを保持」 → s16で明記 ✓
- 「SessionUtil.put/get/delete」 → 実装例s1-s4で明記 ✓
- 「セッションストアにはFormではなくEntityを格納」 → s9で明記 ✓

verify_result = PASS

---

**結論**: 「複数タブでの画面操作を許容するか否か」が判断基準です。複数タブを許容しない場合はDBストア、許容する場合はHIDDENストアを使用します。

**根拠**:

### 選択基準

| 要件 | 使用するストア |
|---|---|
| 入力→確認→完了間でのデータ保持（複数タブ不可） | DBストア |
| 入力→確認→完了間でのデータ保持（複数タブ許容） | HIDDENストア |

### 各ストアの特長

**DBストア**（データベース上のテーブルに保存）
- ローリングメンテナンス等でアプリケーションサーバが停止した場合でもセッション変数の復元が可能
- アプリケーションサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合、後勝ちとなる（先に保存されたデータは消失する）

**HIDDENストア**（クライアントサイド、hiddenタグで画面間を引き回す）
- 複数タブでの画面操作を許容できる
- アプリケーションサーバのヒープ領域を圧迫しない
- 複数スレッドで実行された場合、セッションのデータはそれぞれのスレッドに紐付けて保存される

### HIDDENストアを使う場合のJSP設定

入力・確認画面のJSPに `<n:hiddenStore>` タグを記載する必要があります。

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

### 実装パターン（SessionUtil APIの使用例）

```java
// 入力画面から確認画面へ遷移する際：FormをEntityに変換してセッションストアに保存
ProjectForm form = context.getRequestScopedVar("form");
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);  // ストアは設定のdefaultStoreNameが使用される

// 確認画面から登録処理実行時：セッションストアからEntityを取得して使用
Project project = SessionUtil.get(ctx, "project");
// 登録処理は省略
SessionUtil.delete(ctx, "project");  // 完了後は必ず削除
```

**注意点**:
- セッションストアには **Form ではなく Entity（業務ロジックを実行するためのオブジェクト）を格納**すること。Formを格納すると業務ロジックに不要なデータ変換処理が混入し、密結合なソースが生まれる可能性がある。また、セキュリティの観点からも、バリデーション済みのEntityを保持する方が安全。
- DBストアを使用する場合、`USER_SESSION` テーブルをデータベース上に作成する必要がある。また、ブラウザが閉じられた場合などに期限切れのセッション情報が残るため、定期的に削除する仕組みが必要。
- HIDDENストアを使用し、アプリケーションサーバが冗長化されている場合は、暗号化キーを明示的に設定する必要がある（デフォルトはサーバごとに自動生成）。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s8, libraries-session-store.json:s12, libraries-create-example.json:s2, libraries-create-example.json:s4

---