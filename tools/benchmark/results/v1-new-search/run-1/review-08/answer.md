**結論**: 入力→確認→完了画面間でのセッション変数保持において、DBストアとHIDDENストアの使い分けの判断基準は「複数タブでの画面操作を許容するか否か」である。

**根拠**:

**判断基準の対応表**（`libraries-session-store.json:s9`、`s16` より）:

| 複数タブ操作の許容 | 使用するストア |
|---|---|
| 許容しない | DBストア |
| 許容する | HIDDENストア |

---

**DBストアの特長**（`s16`）:

- 保存先: データベース上のテーブル
- ローリングメンテナンス等でアプリケーションサーバが停止してもセッション変数の復元が可能
- アプリケーションサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合、**後勝ち**になる（先に保存されたデータは消失する）

---

**HIDDENストアの特長**（`s16`）:

- 保存先: クライアントサイド（`hidden` タグを使用して画面間でセッション変数を引き回して実現）
- 複数タブでの画面操作を許容できる
- アプリケーションサーバのヒープ領域を圧迫しない
- 同一セッションの処理が複数スレッドで実行された場合、**それぞれのスレッドに紐付けて**保存される（後勝ちにならない）

---

**HIDDENストア使用時のJSP実装**（`s9`）:

入力・確認画面のJSPに `hiddenStore` タグを配置する:

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

---

**セッションストアへの保存・取得の実装例**（`libraries-create-example.json:s2`）:

```java
// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

**注意点**:

- **セッションストアに保存するのはEntityであること**（`s9`）: FormではなくEntityを格納する。Entityを格納することで、取り出し後すぐ業務ロジックを実行でき、凝集性が高まる。Formは外部入力値を受け付けるためセキュリティ上のリスクもある。
- **HIDDENストアと冗長化環境**（`s12`）: アプリケーションサーバが冗長化されている場合、サーバごとに異なる暗号化キーが生成され復号に失敗することがある。この場合は `HiddenStore` の `encryptor` プロパティで `AesEncryptor` を設定し、明示的に暗号化/復号キーを指定する必要がある。
- **DBストアの後勝ち問題**: 同一セッションで複数スレッドが処理される場合（例：複数タブから同時リクエスト）、後から保存された内容で上書きされる。複数タブを許容する要件ではHIDDENストアを選ぶことでこの問題を回避できる。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s12, libraries-create-example.json:s2

---