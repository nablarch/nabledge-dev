Step 4: `read_sections` = `["component/libraries/libraries-session-store.json:s9", "component/libraries/libraries-session-store.json:s16", "component/libraries/libraries-session-store.json:s2", "component/libraries/libraries-session-store.json:s12"]`

Step 5で回答を生成します。セクションの内容から直接回答できます。

**Step 6: Verify**

回答に含めるNablarch固有の主張を確認します:
- 「複数タブ許容しない → DBストア」→ s9・s16に明示あり ✅
- 「複数タブ許容する → HIDDENストア」→ s9・s16に明示あり ✅
- DBストアの特徴（DBテーブル保存、サーバ停止でも復元可能、後勝ち）→ s16に明示 ✅
- HIDDENストアの特徴（クライアントサイド、hiddenタグで引き回し、複数タブ対応、スレッド別保存）→ s16に明示 ✅
- HIDDENストアはJSPに`<n:hiddenStore>`タグが必要 → s9に明示 ✅
- HIDDENストアのデフォルト暗号化はAES、冗長化時は鍵の明示設定が必要 → s12に明示 ✅
- セッションストアにはFormではなくEntityを格納すること → s9に明示 ✅

verify_result = **PASS**

---

**結論**: 入力→確認→完了画面間のセッション変数保持には、**複数タブでの操作を許容しない場合はDBストア**、**許容する場合はHIDDENストア**を使用します。

**根拠**: セッション変数の保存場所と特性の違いが選択基準です。

**DBストア**（データベース上のテーブル）:
- アプリケーションサーバが停止してもセッション変数を復元できる
- 同一セッションを複数スレッドが処理した場合は後勝ち（先に保存されたデータは消失）
- 複数タブ操作を**許容しない**ユースケースに適切

**HIDDENストア**（クライアントサイド）:
- `hidden`タグを使って画面間でセッション変数を引き回す方式
- 複数タブでの画面操作を**許容できる**
- 同一セッションを複数スレッドが処理した場合、セッションデータはそれぞれのスレッドに紐付けて保存される

選択基準表:

| 用途 | セッションストア |
|---|---|
| 入力～確認～完了（複数タブ許容しない） | DBストア |
| 入力～確認～完了（複数タブ許容する） | HIDDENストア |

HIDDENストアを使用する場合、入力・確認画面のJSPに`<n:hiddenStore>`タグが必要です:

```jsp
<n:form>
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

**注意点**:
- セッションストアに格納するのはFormではなく**Entity**（業務ロジック実行用オブジェクト）を推奨。Formを格納するとバリデーション前の信頼できない値を保持するリスクがある。
- HIDDENストアはデフォルトでAES暗号化を使用するが、アプリケーションサーバが**冗長化**されている場合、サーバごとに異なる鍵が自動生成されるため復号に失敗する。その場合は暗号化/復号キーを明示的に設定する必要がある。

参照: libraries-session-store.json:s9, libraries-session-store.json:s16, libraries-session-store.json:s12

---