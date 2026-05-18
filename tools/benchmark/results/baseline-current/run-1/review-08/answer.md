**結論**: 複数タブでの画面操作を許容するかどうかで使い分けます。許容しない場合はDBストア、許容する場合はHIDDENストアを使用します。

**根拠**:

セッションストアの選択基準（知識ファイルより）:

| 用途 | セッションストア |
|---|---|
| 入力～確認～完了間（複数タブ不許容） | DBストア |
| 入力～確認～完了間（複数タブ許容） | HIDDENストア |

**DBストアの特徴**:
- データはデータベースのテーブルに保存
- ローリングメンテナンス等でAPサーバが停止してもセッション変数を復元可能
- ヒープ領域を圧迫しない
- 同一セッションで複数スレッドが実行された場合、後勝ちになる（先に保存されたデータは消失）

**HIDDENストアの特徴**:
- `hidden` タグを使ってクライアントサイドで画面間引き回す方式
- 複数タブでの画面操作を許容できる
- ヒープ領域を圧迫しない
- 同一セッション・複数スレッドの場合、スレッドごとに独立してデータが保存される

**HIDDENストアを使う場合のJSP実装**（入力・確認画面に必要）:
```jsp
<n:form>
  <n:hiddenStore name="nablarch_hiddenStore" />
</n:form>
```

**セッションストアへの保存実装例**（登録フロー）:
```java
ProjectForm form = context.getRequestScopedVar("form");
Project project = BeanUtil.createAndCopy(Project.class, form);
SessionUtil.put(ctx, "project", project);
```

**注意点**:
- セッションストアには FormではなくEntity（業務ロジック用オブジェクト）を格納すること。Formを格納すると不要なデータ変換処理が業務ロジックに混入し、密結合になりやすい。またFormはバリデーション前の信頼できない値を持つ可能性があるためセキュリティ上も好ましくない。
- HIDDENストアはクライアントサイドにデータを持つため、アプリケーションサーバが冗長化されている場合は暗号化キーを明示的に設定する必要がある（デフォルトはサーバごとに異なるキーが自動生成されるため、復号失敗のリスクあり）。
- DBストアは複数タブ操作時に後勝ちでデータが上書きされる点に注意。

参照: component/libraries/libraries-session-store.json#s9, component/libraries/libraries-session-store.json#s16, component/libraries/libraries-session-store.json#s12, component/libraries/libraries-create-example.json#s2