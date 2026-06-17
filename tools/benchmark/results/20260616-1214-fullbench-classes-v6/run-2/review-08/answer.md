**結論**: 複数タブでの画面操作を許容しない場合は **DBストア**、複数タブを許容する場合は **HIDDENストア** を使用します。

**根拠**:

Nablarchのドキュメントでは、入力→確認→完了画面間のセッション変数保持について、以下の基準で使い分けることが規定されています。

| 用途 | 使用するストア |
|---|---|
| 複数タブでの画面操作を許容しない | **DBストア** |
| 複数タブでの画面操作を許容する | **HIDDENストア** |

**DBストアの特長**:
- データベース上のテーブルにセッション変数を保存する
- ローリングメンテナンス等でAPサーバが停止してもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合は後勝ち（先に保存されたデータは消失）

**HIDDENストアの特長**:
- クライアントサイドに `hidden` タグを使って画面間でセッション変数を引き回す
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 各スレッドに紐付けて保存されるため、複数スレッド実行時もデータが混在しない

**HIDDENストアを使う場合のJSP実装**:

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

**セッションストアへの保存・取得の実装例**（入力→確認画面遷移時）:

```java
// リクエストスコープから入力情報を取得
ProjectForm form = context.getRequestScopedVar("form");

// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

**確認→入力画面へ戻る場合**:

```java
// セッションストアから入力情報を取得
Project project = SessionUtil.get(ctx, "project");

// EntityからFormへ変換
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);

// 入力情報をリクエストスコープに設定
context.setRequestScopedVar("form", form);

// セッションストアから入力情報を削除
SessionUtil.delete(ctx, "project");
```

**注意点**:
- セッションストアには Form ではなく Entity（業務ロジックを実行するオブジェクト）を格納すること。Form を格納すると業務ロジックに不要なデータ変換処理が混入し、密結合なソースが生まれる可能性がある。
- HIDDENストアはデフォルトで AES 暗号化が適用される。APサーバを冗長化している場合は、復号失敗を防ぐために暗号化キーを明示的に設定すること。
- DBストアを使用する場合、`USER_SESSION` テーブルの作成が必要。また期限切れのセッション情報を定期的に削除する必要がある。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s8, libraries-session-store.json:s12, libraries-create-example.json:s1, libraries-create-example.json:s2, libraries-create-example.json:s3