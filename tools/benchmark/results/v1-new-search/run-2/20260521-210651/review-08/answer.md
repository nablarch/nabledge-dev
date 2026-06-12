**結論**: 複数タブでの画面操作を許容するかどうかで使い分ける。許容しない場合はDBストア、許容する場合はHIDDENストアを使用する。

**根拠**:

**選択基準の一覧**（`libraries-session-store.json:s16` より）:

| 用途 | セッションストア |
|---|---|
| 入力～確認～完了画面間（複数タブ許容しない） | DBストア |
| 入力～確認～完了画面間（複数タブ許容する） | HIDDENストア |

**DBストアの特長**（`libraries-session-store.json:s16` より）:
- データベース上のテーブルに保存
- ローリングメンテナンス等でAPサーバが停止した場合でもセッション変数の復元が可能
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合、後勝ちになる（先に保存されたデータは消失する）

**HIDDENストアの特長**（`libraries-session-store.json:s16` より）:
- クライアントサイドに `hidden` タグを使って画面間でセッション変数を引き回して保持
- 複数タブでの画面操作を許容できる
- APサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合、セッションのデータはそれぞれのスレッドに紐付けて保存される

**HIDDENストアを使う場合のJSP実装**（`libraries-session-store.json:s9` より）:

入力・確認画面のJSPに `hiddenStore` タグを追加する:

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

**注意点**:

- DBストアは冗長化APサーバ環境でも問題なく動作するが、HIDDENストアをAPサーバ冗長化環境で使う場合は、デフォルトでサーバごとに異なる暗号化キーが生成されるため、明示的に共通のキーを設定する必要がある（`libraries-session-store.json:s12`）。
- セッションストアには Form ではなく Entity（業務ロジックを実行するためのオブジェクト）を格納することを推奨する（`libraries-session-store.json:s9`）。
- `SessionStoreHandler` でHIDDENストアを使用する場合、ハンドラの配置順に制約がある。`マルチパートリクエストハンドラ` より後ろ、かつ `内部フォーワードハンドラ` より前に配置する必要がある（`handlers-SessionStoreHandler.json:s3`）。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s12, handlers-SessionStoreHandler.json:s3

---