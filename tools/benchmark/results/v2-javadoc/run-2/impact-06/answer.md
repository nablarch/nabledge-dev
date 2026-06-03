十分な情報が揃いました。Step 5 — 回答を生成します。

---

**結論**: スケールアウト環境では **DBストア・HIDDENストア・Redisストア** が選択肢となる。HTTPセッションストアはAPサーバが状態を保持するため、そのままではスケールアウトに対応できない。

**根拠**:

Nablarchのセッションストアには以下の4種類がある。

**DBストア（推奨度: 高）**
- データベース上のテーブル (`USER_SESSION`) に保存
- APサーバが停止してもセッション変数の復元が可能（ローリングメンテナンス対応）
- APサーバのヒープ領域を圧迫しない
- 同一セッションが複数スレッドで実行された場合は後勝ち（先に保存されたデータは消失）
- 期限切れのセッション情報は定期的に削除するバッチが必要

**HIDDENストア（スケールアウト対応可・注意あり）**
- クライアントサイドに保存（`hidden` タグで画面間を引き回す）
- APサーバに状態を持たないためスケールアウト対応
- 複数タブでの画面操作を許容できる
- **⚠️ 冗長化環境での注意**: デフォルトでは暗号化キーをAPサーバごとに自動生成するため、復号に失敗するケースがある。明示的に共通キーを設定する必要がある。

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

**Redisストア（Lettuce アダプタ）（推奨度: 高）**
- 特徴はDBストアと同じ（保存先が異なるだけ）
- DBストアに対するメリット:
  - セッション情報保存用テーブルを事前に用意する必要がない
  - Redisの有効期限機能で期限切れのセッション情報が自動削除されるため、削除バッチが不要

**HTTPセッションストア（スケールアウト非推奨）**
- APサーバのヒープ領域に保存
- APサーバごとに情報を保持するため、スケールアウト時にスティッキーセッション・セッションレプリケーション等の工夫が必要
- これらはAPサーバ依存または廃棄容易性の面で劣る

各ストアの選択基準:

| 用途 | 推奨ストア |
|---|---|
| 入力〜確認〜完了画面間での入力情報保持（複数タブ不可） | DBストア |
| 入力〜確認〜完了画面間での入力情報保持（複数タブ対応） | HIDDENストア |
| 認証情報の保持 | DBストアまたはHTTPセッションストア |

**注意点**:
- セッションの **有効期間** はデフォルトでHTTPセッションに保存される。スケールアウト環境では有効期間の保存先をデータベースに変更する設定が必要（`SessionStoreHandler` の設定）。
- DBストアを使用する場合、Oracleでは `SESSION_ID` カラムを `CHAR` ではなく `VARCHAR` で定義すること。

参照: `libraries-session-store.json:s2`, `libraries-session-store.json:s16`, `libraries-session-store.json:s12`, `libraries-session-store.json:s17`, `libraries-stateless-web-app.json:s1`, `adapters-redisstore-lettuce-adaptor.json:s15`

---