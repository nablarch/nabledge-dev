**結論**: 複数タブでの画面操作を許容しない場合はDBストア、許容する場合はHIDDENストアを使用する。

**根拠**:

セッションストアの選択基準:

| 用途 | セッションストア |
|---|---|
| 入力〜確認〜完了画面間（複数タブを許容しない） | DBストア |
| 入力〜確認〜完了画面間（複数タブを許容する） | HIDDENストア |

**DBストアの仕組み**:
- セッション変数をデータベース上の `USER_SESSION` テーブルに保持する
- APサーバが停止してもセッション変数の復元が可能
- 同一セッションで複数スレッドが実行された場合、**後勝ち**になる（先のデータは消失する）
- そのため、同一ユーザが複数タブで操作すると競合が発生する

**HIDDENストアの仕組み**:
- セッション変数をクライアントサイド（`hidden`タグ）で画面間を引き回す
- 複数タブごとに独立したデータを持てるため、マルチタブ操作に対応できる
- 同一セッションの複数スレッドでも、それぞれのスレッドに紐付けて保存される

HIDDENストアを使用する場合、入力・確認画面のJSPに `<n:hiddenStore>` タグを配置する必要がある:

```jsp
<n:form>
  <n:hiddenStore name="nablarch_hiddenStore" />
  <!-- その他のタグは省略 -->
</n:form>
```

HIDDENストアのデフォルト暗号化はAES（サーバ内で自動生成したキー）。APサーバを冗長化している場合はサーバごとにキーが異なり復号に失敗するため、暗号化キーを明示的に設定する必要がある:

```xml
<component class="nablarch.common.web.session.store.HiddenStore">
  <property name="encryptor">
    <component class="nablarch.common.encryption.AesEncryptor">
      <property name="base64Key">
        <component class="nablarch.common.encryption.Base64Key">
          <property name="key" value="OwYMOWbnLyYy93P8oIayeg==" />
          <property name="iv" value="NOj5OUN+GlyGYTc6FM0+nw==" />
        </component>
      </property>
    </component>
  </property>
</component>
```

**注意点**:
- セッションストアに保存するオブジェクトはシリアライズ可能なJava Beansであること
- セッションストアにはFormではなくEntity（業務ロジック用オブジェクト）を格納することを推奨。Formはバリデーション前の信頼できない値を持つ可能性があるため、セキュリティ上のリスクになる
- DBストアを使用する場合、ブラウザを閉じてもDBにセッション情報が残るため、期限切れデータの定期削除が必要

参照:
- `component/libraries/libraries-session-store.json:s9` — 入力〜確認〜完了画面間での使い分け
- `component/libraries/libraries-session-store.json:s16` — セッションストアの特長と選択基準
- `component/libraries/libraries-session-store.json:s12` — HIDDENストアの暗号化設定

---